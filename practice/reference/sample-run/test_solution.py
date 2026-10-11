"""Offline tests for solution.py: tools, refund rules, approval pause and Reply retry.

Each test uses a scripted fake model, so no API key is needed and runs are deterministic.
"""

import copy
import json
from pathlib import Path

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.types import Command
from pydantic import ValidationError

from solution import Reply, build_agent, make_tools, refund_refusal

DATA = json.loads((Path(__file__).parent / "kit/practice/data.json").read_text())


class ScriptedModel(GenericFakeChatModel):
    """Fake chat model that replays fixed messages; bind_tools is a no-op."""

    def bind_tools(self, tools, **kwargs):
        """Ignore tools: the script already names them."""
        return self


def fresh_shop():
    """A deep copy of data.json with an empty refunds list, as the grader builds it."""
    shop = copy.deepcopy(DATA)
    shop["refunds"] = []
    return shop


def tools_by_name(shop):
    """The three tools for this shop, keyed by name."""
    return {t.name: t for t in make_tools(shop)}


def call(name, args, i=0):
    """An AI message calling one tool."""
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": f"c{i}"}])


def run(shop, script, text, human=None, thread="t"):
    """Run the agent, resuming with `human` while it is paused; return (result, pauses)."""
    graph = build_agent(ScriptedModel(messages=iter(script)), shop)
    cfg = {"configurable": {"thread_id": thread}}
    out = graph.invoke({"messages": [HumanMessage(text)]}, cfg)
    pauses = 0
    while out.get("__interrupt__"):
        pauses += 1
        assert pauses <= 3, "resume never reached the end"
        out = graph.invoke(Command(resume=human), cfg)
    return out, pauses


def tool_texts(out):
    """All tool outputs of a run, in order."""
    return [m.content for m in out["messages"] if isinstance(m, ToolMessage)]


def test_get_order_formats():
    """Delivered shows the date, processing does not, unknown gives not-found; ids are normalized."""
    t = tools_by_name(fresh_shop())["get_order"]
    assert t.invoke({"order_id": "A-101"}) == "A-101: Desk lamp, $30, delivered 2026-02-20"
    assert t.invoke({"order_id": "A-103"}) == "A-103: Monitor, $80, processing"
    assert t.invoke({"order_id": "A-999"}) == "Order A-999 not found."
    assert t.invoke({"order_id": " a-102 "}).startswith("A-102: Office chair, $120")


def test_search_policy_ranks_best_first():
    """Shipping query puts P-2 first (not data order); at most 2 lines; nonsense finds nothing."""
    t = tools_by_name(fresh_shop())["search_policy"]
    lines = t.invoke({"query": "when will my package ship? shipping is slow"}).splitlines()
    assert lines[0].startswith("P-2: Shipping")
    assert len(lines) <= 2
    damaged = t.invoke({"query": "my lamp arrived damaged"}).splitlines()
    assert damaged[0].startswith("P-3: Damaged")
    refund = t.invoke({"query": "refund"}).splitlines()
    assert refund[0].startswith("P-1: ") and len(refund) <= 2
    assert t.invoke({"query": "hello there"}) == "No matching policy."


def test_refund_rules_in_order():
    """Each of rules 1-4 gives its exact text; an old order over $50 is refused, never paused."""
    shop = fresh_shop()
    shop["orders"]["A-105"] = {"item": "Desk", "amount": 300, "status": "delivered", "delivered_on": "2026-01-01"}
    assert refund_refusal(shop, "A-999") == "Order A-999 not found."
    assert refund_refusal(shop, "A-103") == "Not eligible: A-103 has not been delivered."
    assert refund_refusal(shop, "A-104") == "Not eligible: A-104 was delivered 50 days ago (limit 30)."
    assert refund_refusal(shop, "A-105") == "Not eligible: A-105 was delivered 59 days ago (limit 30)."
    shop["refunds"].append("A-104")  # already refunded is checked before age
    assert refund_refusal(shop, "A-104") == "A-104 was already refunded."
    assert refund_refusal(shop, "A-101") is None
    # boundary: exactly 30 days is allowed, 31 is not
    shop["orders"]["A-106"] = {"item": "Pen", "amount": 5, "status": "delivered", "delivered_on": "2026-01-30"}
    shop["orders"]["A-107"] = {"item": "Pen", "amount": 5, "status": "delivered", "delivered_on": "2026-01-29"}
    assert refund_refusal(shop, "A-106") is None
    assert refund_refusal(shop, "A-107") == "Not eligible: A-107 was delivered 31 days ago (limit 30)."


def final(category, order_id, action, policy_ids, i=9):
    """An AI message calling Reply."""
    return call("Reply", {"category": category, "order_id": order_id, "action": action,
                          "policy_ids": policy_ids}, i)


def test_small_refund_recorded_once():
    """$30 refund goes through without a pause and is recorded once; a second request is refused."""
    shop = fresh_shop()
    script = [call("request_refund", {"order_id": "A-101", "reason": "broken"}, 0),
              call("request_refund", {"order_id": "A-101", "reason": "again"}, 1),
              final("refund", "A-101", "Refunded order A-101.", ["P-1"])]
    out, pauses = run(shop, script, "refund A-101")
    assert pauses == 0
    assert shop["refunds"] == ["A-101"]
    assert tool_texts(out)[:2] == ["Refunded A-101 ($30).", "A-101 was already refunded."]
    assert out["structured_response"] == Reply(category="refund", order_id="A-101",
                                               action="Refunded order A-101.", policy_ids=["P-1"])


def test_large_refund_approved_after_pause():
    """$120 refund pauses, and on 'yes' is recorded exactly once (the tool re-runs on resume)."""
    shop = fresh_shop()
    script = [call("request_refund", {"order_id": "A-102", "reason": "too big"}, 0),
              final("refund", "A-102", "Refunded A-102 after approval.", ["P-1"])]
    out, pauses = run(shop, script, "refund my chair A-102", human="yes")
    assert pauses == 1
    assert shop["refunds"] == ["A-102"]
    assert "Refunded A-102 ($120) after approval." in tool_texts(out)
    assert out["structured_response"].order_id == "A-102"


def test_large_refund_declined_records_nothing():
    """On 'no' the refund is declined and nothing is recorded."""
    shop = fresh_shop()
    script = [call("request_refund", {"order_id": "A-102", "reason": "too big"}, 0),
              final("refund", "A-102", "The reviewer declined the refund.", ["P-1"])]
    out, pauses = run(shop, script, "refund A-102", human="no")
    assert pauses == 1
    assert shop["refunds"] == []
    assert "Refund for A-102 declined by reviewer." in tool_texts(out)


def test_invalid_reply_is_retried():
    """A Reply with a bad category is sent back; the model's second, valid Reply is returned."""
    shop = fresh_shop()
    script = [final("billing", "A-101", "Checked the order.", [], 0),
              final("other", None, "Answered the question.", [], 1)]
    out, _ = run(shop, script, "hi")
    reply = out["structured_response"]
    assert reply.category == "other" and reply.order_id is None
    assert any("validation error for Reply" in t for t in tool_texts(out)), "first Reply was not rejected"


def test_reply_rejects_bad_fields():
    """Bad order id form and a two-sentence action are invalid."""
    with pytest.raises(ValidationError):
        Reply(category="refund", order_id="101", action="Refunded.", policy_ids=[])
    with pytest.raises(ValidationError):
        Reply(category="refund", order_id="A-101", action="Refunded it. Thanks!", policy_ids=[])
