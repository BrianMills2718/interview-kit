"""Offline tests for examples/patterns.py. Each would fail if its pattern were broken."""

import sys
from pathlib import Path

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolMessage

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
import patterns  # noqa: E402
from patterns import OrderAnswer, build_refund_graph, build_structured_agent, run_refund, search_docs  # noqa: E402


class FakeToolModel(GenericFakeChatModel):
    """Fake chat model that accepts bind_tools and replays scripted replies."""

    def bind_tools(self, tools, **kwargs):
        return self


def call(name, args, i="1"):
    return AIMessage("", tool_calls=[{"name": name, "args": args, "id": i}])


def test_structured_output_retries_on_invalid_then_validates():
    replies = [
        call("search_docs", {"query": "how fast do orders ship"}, "1"),
        call("OrderAnswer", {"order_id": "A-100", "status": "lost", "source": "kb-2"}, "2"),  # invalid
        call("OrderAnswer", {"order_id": "A-100", "status": "shipped", "source": "kb-2"}, "3"),
    ]
    agent = build_structured_agent(FakeToolModel(messages=iter(replies)), tools=[search_docs])
    out = agent.invoke({"messages": [("user", "Where is A-100?")]})
    assert out["structured_response"] == OrderAnswer(order_id="A-100", status="shipped", source="kb-2")
    errors = [m for m in out["messages"] if isinstance(m, ToolMessage) and "validation error" in m.content]
    assert len(errors) == 1  # the invalid answer was sent back to the model, not accepted


def test_retrieval_ranks_the_relevant_document_first():
    hits = search_docs.invoke({"query": "can I get a refund after delivery", "k": 2}).splitlines()
    assert hits[0].startswith("kb-1:")


def test_retrieval_says_so_when_nothing_matches():
    assert search_docs.invoke({"query": "zebra"}) == "No matching documents."


def test_interrupt_pauses_before_the_action_and_resume_yes_runs_it():
    patterns.REFUNDS_ISSUED.clear()
    paused, final = run_refund(build_refund_graph(), "A-100", "yes", thread="yes")
    assert paused["__interrupt__"][0].value == {"question": "Refund order A-100?"}
    assert patterns.REFUNDS_ISSUED == ["A-100"]
    assert final["messages"][-1].content == "Refund issued for A-100."


def test_interrupt_resume_no_skips_the_action():
    patterns.REFUNDS_ISSUED.clear()
    _, final = run_refund(build_refund_graph(), "A-101", "no", thread="no")
    assert patterns.REFUNDS_ISSUED == []
    assert final["messages"][-1].content == "Refund for A-101 was not approved."
