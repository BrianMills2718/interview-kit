"""Offline tests for solution.py: tool rules, Reply validation, approval gate through the graph."""

import copy
import json
from pathlib import Path

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command
from pydantic import ValidationError

import solution

DATA = json.loads((Path(__file__).parent / "kit/practice/data.json").read_text())


def fresh_shop():
    """A deep copy of the data with an empty refunds list, as the grader builds it."""
    shop = copy.deepcopy(DATA)
    shop["refunds"] = []
    return shop


def tools(shop):
    """Tool name -> callable for direct testing."""
    return {t.name: t for t in solution.make_tools(shop)}


class Scripted(GenericFakeChatModel):
    """Fake model whose bind_tools is a no-op (GenericFakeChatModel raises otherwise)."""

    def bind_tools(self, tools, **kw):
        return self


def scripted(*steps):
    """Build a fake model from (tool_name, args) lists per turn."""
    msgs = [AIMessage(content="", tool_calls=[{"name": n, "args": a, "id": f"c{i}_{j}"} for j, (n, a) in enumerate(s)])
            for i, s in enumerate(steps)]
    return Scripted(messages=iter(msgs))


def test_get_order_delivered_and_not():
    t = tools(fresh_shop())
    assert t["get_order"].invoke({"order_id": "A-101"}) == "A-101: Desk lamp, $30, delivered 2026-02-20"
    assert t["get_order"].invoke({"order_id": "A-103"}) == "A-103: Monitor, $80, processing"
    assert t["get_order"].invoke({"order_id": "A-999"}) == "Order A-999 not found."


def test_search_policy_best_first_and_none():
    t = tools(fresh_shop())
    out = t["search_policy"].invoke({"query": "refund delivered"})
    assert out.splitlines()[0].startswith("P-1: Refunds:")
    assert len(out.splitlines()) <= 2
    assert t["search_policy"].invoke({"query": "zzz qqq"}) == "No matching policy."


@pytest.mark.parametrize("oid,expected", [
    ("A-999", "Order A-999 not found."),
    ("A-103", "Not eligible: A-103 has not been delivered."),
    ("A-104", "Not eligible: A-104 was delivered 50 days ago (limit 30)."),
    ("A-101", "Refunded A-101 ($30)."),
])
def test_refund_rules(oid, expected):
    shop = fresh_shop()
    assert tools(shop)["request_refund"].invoke({"order_id": oid, "reason": "x"}) == expected
    assert shop["refunds"] == (["A-101"] if oid == "A-101" else [])


def test_refund_rules_already_refunded_beats_not_delivered():
    shop = fresh_shop()
    shop["refunds"] = ["A-103"]  # rule 2 is checked before rule 3
    assert tools(shop)["request_refund"].invoke({"order_id": "A-103", "reason": "x"}) == "A-103 was already refunded."


def test_reply_rejects_bad_id_and_category():
    solution.Reply(category="refund", order_id="A-101", action="Refunded.", policy_ids=["P-1"])
    with pytest.raises(ValidationError):
        solution.Reply(category="refund", order_id="101", action="x", policy_ids=[])
    with pytest.raises(ValidationError):
        solution.Reply(category="billing", order_id=None, action="x", policy_ids=[])


def run(shop, llm, answer):
    """Invoke the graph, resuming each interrupt with answer; returns (result, interrupts)."""
    g = solution.build_agent(llm, shop)
    cfg = {"configurable": {"thread_id": "t"}, "recursion_limit": 20}
    out, n = g.invoke({"messages": [HumanMessage("refund A-102")]}, cfg), 0
    while out.get("__interrupt__"):
        n += 1
        out = g.invoke(Command(resume=answer), cfg)
    return out, n


REPLY = ("Reply", {"category": "refund", "order_id": "A-102", "action": "Handled refund.", "policy_ids": ["P-1"]})


@pytest.mark.parametrize("answer,refunds,text", [
    ("yes", ["A-102"], "Refunded A-102 ($120) after approval."),
    ("no", [], "Refund for A-102 declined by reviewer."),
])
def test_big_refund_needs_yes(answer, refunds, text):
    shop = fresh_shop()
    out, n = run(shop, scripted([("request_refund", {"order_id": "A-102", "reason": "broken"})], [REPLY]), answer)
    assert n == 1
    assert shop["refunds"] == refunds  # exactly once: the tool re-runs on resume
    assert any(m.content == text for m in out["messages"])
    assert out["structured_response"].order_id == "A-102"


def test_invalid_reply_goes_back_to_model():
    shop = fresh_shop()
    bad = ("Reply", {"category": "refund", "order_id": "bad", "action": "x", "policy_ids": []})
    out, _ = run(shop, scripted([bad], [REPLY]), "yes")
    assert out["structured_response"].order_id == "A-102"
