"""Offline tests for the hardening middleware: each case fails if its protection is removed."""

import sys
from pathlib import Path

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from hardening import ask_with_cost, build_agent  # noqa: E402


class FakeToolModel(GenericFakeChatModel):
    """Fake chat model that accepts bind_tools and records what it was sent."""

    seen: list = []

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, *args, **kwargs):
        self.seen.append(list(messages))
        return super()._generate(messages, *args, **kwargs)


class FlakyModel(FakeToolModel):
    """Raises once (like a 503 or rate limit), then answers."""

    failures: int = 1

    def _generate(self, messages, *args, **kwargs):
        if self.failures:
            self.failures -= 1
            raise ConnectionError("simulated 503")
        return super()._generate(messages, *args, **kwargs)


def call(order_id, n=1):
    return AIMessage("", tool_calls=[{"name": "lookup_order", "args": {"order_id": order_id}, "id": f"c{n}"}])


def test_email_is_redacted_before_the_model_sees_it():
    llm = FakeToolModel(messages=iter([AIMessage("ok")]), seen=[])
    build_agent(llm).invoke({"messages": [("user", "Order A-100, reply to jo@example.com")]})
    sent = " ".join(str(m.content) for m in llm.seen[0] if isinstance(m, HumanMessage))
    assert "jo@example.com" not in sent and "REDACTED" in sent.upper()


def test_transient_model_error_is_retried():
    llm = FlakyModel(messages=iter([AIMessage("A-100 has shipped.")]), seen=[])
    answer, _ = ask_with_cost(build_agent(llm, initial_delay=0), "Where is A-100?")
    assert answer == "A-100 has shipped." and llm.failures == 0


def test_runaway_tool_loop_is_stopped_by_the_call_limit():
    llm = FakeToolModel(messages=iter([call("A-100", i) for i in range(50)]), seen=[])
    out = build_agent(llm).invoke({"messages": [("user", "loop")]}, {"recursion_limit": 100})
    assert len(llm.seen) == 6  # run_limit=6 model calls, then the agent ends instead of looping
    assert out["messages"]


def test_oversized_input_is_rejected_without_a_model_call():
    llm = FakeToolModel(messages=iter([AIMessage("should not be called")]), seen=[])
    answer, usage = ask_with_cost(build_agent(llm), "x" * 5000)
    assert answer.startswith("Request too long") and llm.seen == []
    assert usage == {"input_tokens": 0, "output_tokens": 0, "usd": 0.0}


def test_usage_is_counted_from_the_model_response():
    # the callback only counts messages whose response_metadata names the model (real providers set it)
    reply = AIMessage(
        "done",
        usage_metadata={"input_tokens": 1000, "output_tokens": 1000, "total_tokens": 2000},
        response_metadata={"model_name": "fake"},
    )
    llm = FakeToolModel(messages=iter([reply]), seen=[])
    _, usage = ask_with_cost(build_agent(llm), "hi")
    assert usage["input_tokens"] == 1000 and usage["output_tokens"] == 1000
    assert usage["usd"] == pytest.approx(0.00075)
