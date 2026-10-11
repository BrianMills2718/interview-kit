"""Offline tests for solution.py: tools, refund rules, approval pause, Reply validation, wiring."""

import copy
import json
from pathlib import Path

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.errors import GraphRecursionError
from langgraph.types import Command
from pydantic import ValidationError

import solution

DATA = json.loads((Path(__file__).parent / "kit/practice/data.json").read_text())


class Scripted(GenericFakeChatModel):
    """Fake model replaying fixed messages; bind_tools is a no-op."""

    def bind_tools(self, tools, **kw):
        """Return self so create_agent can bind tools."""
        return self


def fresh_shop():
    """A copy of the shop data with an empty refunds list."""
    shop = copy.deepcopy(DATA)
    shop["refunds"] = []
    return shop


def tools(shop):
    """Tools by name for direct calls."""
    return {t.name: t for t in solution.make_tools(shop)}


def call(name, **args):
    """A scripted AI message calling one tool."""
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": f"{name}-{len(args)}"}])


def run(shop, script, text="help", human=None, thread="t"):
    """Invoke the agent with a script; resume each pause with `human`; return (result, pauses)."""
    graph = solution.build_agent(Scripted(messages=iter(script)), shop)
    cfg = {"configurable": {"thread_id": thread}}
    out, pauses = graph.invoke({"messages": [HumanMessage(text)]}, cfg), []
    while out.get("__interrupt__"):
        pauses.append(out["__interrupt__"][0].value)
        out = graph.invoke(Command(resume=human), cfg)
    return out, pauses


def reply(**kw):
    """A scripted final Reply call."""
    base = {"category": "refund", "order_id": "A-101", "action": "Refunded the order.", "policy_ids": ["P-1"]}
    return call("Reply", **{**base, **kw})


def test_get_order_delivered_and_missing():
    t = tools(fresh_shop())["get_order"]
    assert t.invoke({"order_id": "A-101"}) == "A-101: Desk lamp, $30, delivered 2026-02-20"
    assert t.invoke({"order_id": "A-103"}) == "A-103: Monitor, $80, processing"
    assert t.invoke({"order_id": "A-999"}) == "Order A-999 not found."


def test_refund_rules_in_order():
    shop = fresh_shop()
    r = tools(shop)["request_refund"]
    ask = lambda oid: r.invoke({"order_id": oid, "reason": "x"})  # noqa: E731
    assert ask("A-999") == "Order A-999 not found."
    assert ask("A-103") == "Not eligible: A-103 has not been delivered."
    assert ask("A-104") == "Not eligible: A-104 was delivered 50 days ago (limit 30)."
    assert ask("A-101") == "Refunded A-101 ($30)."
    # rule 2 is checked before rule 4: an old order already refunded says "already refunded"
    shop["refunds"].append("A-104")
    assert ask("A-104") == "A-104 was already refunded."
    assert ask("A-101") == "A-101 was already refunded."
    assert shop["refunds"] == ["A-101", "A-104"]


def test_large_refund_pauses_then_approves():
    shop = fresh_shop()
    out, pauses = run(shop, [call("request_refund", order_id="A-102", reason="broken"),
                             reply(order_id="A-102", action="Refunded after approval.")], human="yes")
    assert len(pauses) == 1 and pauses[0]["amount"] == 120 and pauses[0]["order_id"] == "A-102"
    assert shop["refunds"] == ["A-102"]  # once, although the tool ran twice
    assert "Refunded A-102 ($120) after approval." in [m.content for m in out["messages"]]


def test_large_refund_declined_records_nothing():
    shop = fresh_shop()
    out, pauses = run(shop, [call("request_refund", order_id="A-102", reason="broken"),
                             reply(order_id="A-102", action="The reviewer declined the refund.")], human="no")
    assert len(pauses) == 1
    assert shop["refunds"] == []
    assert "Refund for A-102 declined by reviewer." in [m.content for m in out["messages"]]


def test_search_policy_best_first_and_no_match():
    s = tools(fresh_shop())["search_policy"]
    lines = s.invoke({"query": "how long does shipping take"}).splitlines()
    assert lines[0].startswith("P-2: Shipping") and len(lines) <= 2
    assert len(s.invoke({"query": "refund damaged item delivered"}).splitlines()) == 2
    assert s.invoke({"query": "zebra giraffe"}) == "No matching policy."


def test_reply_rejects_bad_values():
    solution.Reply(category="refund", order_id="A-101", action="Refunded it.", policy_ids=["P-1"])
    for bad in ({"category": "billing"}, {"order_id": "101"}, {"action": "Done. Also more."},
                {"policy_ids": ["refunds"]}, {"action": "  "}):
        args = {"category": "refund", "order_id": "A-101", "action": "Refunded it.", "policy_ids": [], **bad}
        with pytest.raises(ValidationError):
            solution.Reply(**args)


def test_agent_end_to_end_small_refund():
    shop = fresh_shop()
    out, pauses = run(shop, [call("get_order", order_id="A-101"),
                             call("request_refund", order_id="A-101", reason="unwanted"), reply()])
    assert pauses == [] and shop["refunds"] == ["A-101"]
    assert out["structured_response"].order_id == "A-101"


def test_invalid_reply_goes_back_for_retry():
    shop = fresh_shop()
    out, _ = run(shop, [reply(category="billing"), reply(category="other", order_id=None, policy_ids=[])])
    assert out["structured_response"].category == "other"
    errors = [m.content for m in out["messages"] if m.type == "tool" and "validation error" in m.content]
    assert len(errors) == 1 and "category" in errors[0]  # the first, invalid Reply went back to the model


def test_looping_model_is_stopped():
    shop = fresh_shop()
    with pytest.raises(GraphRecursionError):
        run(shop, [call("get_order", order_id="A-101")] * 50)
