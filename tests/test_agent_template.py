"""Offline tests for the agent template using a scripted fake model."""

import sys
from pathlib import Path

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolMessage

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from agent_template import build_graph  # noqa: E402


class FakeToolModel(GenericFakeChatModel):
    """Fake chat model that accepts bind_tools and replays scripted replies."""

    def bind_tools(self, tools, **kwargs):
        return self


def run(replies, question="Where is order A-100?"):
    graph = build_graph(FakeToolModel(messages=iter(replies)))
    return graph.invoke({"messages": [("user", question)]}, config={"recursion_limit": 10})["messages"]


def call(order_id):
    return AIMessage("", tool_calls=[{"name": "lookup_order", "args": {"order_id": order_id}, "id": "1"}])


def test_tool_result_reaches_the_model():
    msgs = run([call("A-100"), AIMessage("Order A-100 has shipped.")])
    tool_msgs = [m for m in msgs if isinstance(m, ToolMessage)]
    assert tool_msgs[0].content == "Order A-100: shipped"
    assert msgs[-1].content == "Order A-100 has shipped."


def test_tool_error_is_returned_not_raised():
    msgs = run([call("Z-9"), AIMessage("I could not find that order.")])
    tool_msgs = [m for m in msgs if isinstance(m, ToolMessage)]
    assert "Unknown order id 'Z-9'" in tool_msgs[0].content
    assert msgs[-1].content == "I could not find that order."


def test_no_tool_needed_ends_immediately():
    msgs = run([AIMessage("Hello!")], question="hi")
    assert not any(isinstance(m, ToolMessage) for m in msgs)
    assert msgs[-1].content == "Hello!"
