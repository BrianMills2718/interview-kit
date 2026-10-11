"""Offline tests for the supervisor and streaming patterns, using scripted fake models."""

import sys
from pathlib import Path

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolMessage

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from agent_template import build_graph  # noqa: E402
from patterns_multi import build_supervisor, specialist_tool, stream_steps  # noqa: E402


class FakeToolModel(GenericFakeChatModel):
    """Fake chat model that accepts bind_tools and replays scripted replies."""

    def bind_tools(self, tools, **kwargs):
        return self


def fake(*replies):
    return FakeToolModel(messages=iter(replies))


def call(name, **args):
    return AIMessage("", tool_calls=[{"name": name, "args": args, "id": name + "-1"}])


def supervisor_with(sup_replies, orders_replies, policy_replies):
    """Two specialists: one with the order-lookup tool (the template agent), one plain."""
    orders = specialist_tool("orders", "Knows order status. Ask with the order id.",
                             build_graph(fake(*orders_replies)))
    policy = specialist_tool("policy", "Knows refund and return policy.",
                             build_graph(fake(*policy_replies)))
    return build_supervisor(fake(*sup_replies), [orders, policy], "Route each question to a specialist.")


def test_supervisor_routes_to_the_right_specialist_and_uses_its_answer():
    graph = supervisor_with(
        sup_replies=[call("ask_orders", question="Status of A-100?"), AIMessage("A-100 has shipped.")],
        orders_replies=[call("lookup_order", order_id="A-100"), AIMessage("Order A-100 is shipped.")],
        policy_replies=[AIMessage("POLICY SHOULD NOT BE ASKED")],
    )
    msgs = graph.invoke({"messages": [("user", "Where is A-100?")]}, config={"recursion_limit": 10})["messages"]
    tool_msgs = [m for m in msgs if isinstance(m, ToolMessage)]
    assert [m.name for m in tool_msgs] == ["ask_orders"]
    # the specialist ran its own tool loop, and its final answer came back to the supervisor
    assert tool_msgs[0].content == "Order A-100 is shipped."
    assert msgs[-1].content == "A-100 has shipped."


def test_supervisor_can_ask_two_specialists_in_turn():
    graph = supervisor_with(
        sup_replies=[call("ask_orders", question="Status of A-101?"),
                     call("ask_policy", question="Can a processing order be cancelled?"),
                     AIMessage("A-101 is processing and can still be cancelled.")],
        orders_replies=[call("lookup_order", order_id="A-101"), AIMessage("Order A-101 is processing.")],
        policy_replies=[AIMessage("Processing orders can be cancelled.")],
    )
    msgs = graph.invoke({"messages": [("user", "Can I cancel A-101?")]}, config={"recursion_limit": 10})["messages"]
    tool_msgs = [m for m in msgs if isinstance(m, ToolMessage)]
    assert [(m.name, m.content) for m in tool_msgs] == [
        ("ask_orders", "Order A-101 is processing."),
        ("ask_policy", "Processing orders can be cancelled."),
    ]


def test_stream_yields_each_step_in_order():
    graph = build_graph(fake(call("lookup_order", order_id="A-100"), AIMessage("Order A-100 has shipped.")))
    steps = list(stream_steps(graph, "Where is A-100?"))
    assert steps == [
        ("agent", "calls ['lookup_order']"),
        ("tools", "Order A-100: shipped"),
        ("agent", "Order A-100 has shipped."),
    ]
