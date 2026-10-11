"""Order-support agent for a small shop: three tools, a human-approval pause for big refunds,
and a validated `Reply` as the final answer (LangChain `create_agent` on LangGraph)."""

import logging
import re
from datetime import date
from typing import Literal, Optional

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from pydantic import BaseModel, Field, field_validator

log = logging.getLogger("support_agent")

SYSTEM_PROMPT = (
    "You are a support agent for a small shop. Use get_order for order facts, search_policy for "
    "policy text and request_refund to refund; never guess a fact. Finish by calling Reply."
)
STOP_WORDS = {"a", "an", "the", "and", "or", "to", "of", "in", "on", "for", "is", "it", "my", "i",
              "with", "can", "be", "we", "you", "do", "how", "what", "if", "me", "was", "this"}
REFUND_LIMIT_DAYS = 30
APPROVAL_OVER = 50


class Reply(BaseModel):
    """The validated final answer the agent returns to the customer."""

    category: Literal["refund", "shipping", "damaged", "other"]
    order_id: Optional[str] = Field(None, description="Order id in A-123 form, or null if none")
    action: str = Field(description="One sentence saying what was done")
    policy_ids: list[str] = Field(default_factory=list, description="Ids like P-1 of policies used")

    @field_validator("order_id")
    @classmethod
    def order_id_form(cls, v: Optional[str]) -> Optional[str]:
        """Reject order ids not in A-123 form, so the model retries with a real id."""
        if v is not None and not re.fullmatch(r"A-\d+", v):
            raise ValueError(f"order_id must look like A-123, got {v!r}")
        return v

    @field_validator("action")
    @classmethod
    def one_sentence(cls, v: str) -> str:
        """Reject an empty action or one with more than one sentence."""
        v = v.strip()
        if not v or re.search(r"[.!?]\s+\S", v):
            raise ValueError("action must be exactly one non-empty sentence")
        return v

    @field_validator("policy_ids")
    @classmethod
    def policy_id_form(cls, v: list[str]) -> list[str]:
        """Reject policy ids not in P-1 form."""
        bad = [p for p in v if not re.fullmatch(r"P-\d+", p)]
        if bad:
            raise ValueError(f"policy_ids must look like P-1, got {bad}")
        return v


def words(text: str) -> set[str]:
    """Lowercase content words of text, for policy matching."""
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP_WORDS}


def make_tools(shop: dict) -> list:
    """Build the three tools as closures over this shop, so each run writes its own refunds list."""
    orders = shop["orders"]
    today = date.fromisoformat(shop["today"])

    @tool
    def get_order(order_id: str) -> str:
        """Look up an order by id (e.g. 'A-101'): item, amount, status, and delivery date once delivered."""
        o = orders.get(order_id)
        if o is None:
            out = f"Order {order_id} not found."
        elif o["status"] == "delivered":
            out = f"{order_id}: {o['item']}, ${o['amount']}, delivered {o['delivered_on']}"
        else:
            out = f"{order_id}: {o['item']}, ${o['amount']}, {o['status']}"
        log.info("tool get_order(%s) -> %d chars", order_id, len(out))
        return out

    @tool
    def search_policy(query: str) -> str:
        """Find up to 2 shop policies matching the query, best first, as lines 'P-1: <text>'."""
        q = words(query)
        scored = [(len(q & words(p["text"])), i, p) for i, p in enumerate(shop["policies"])]
        # sort by score, then original order; rejected: embeddings, a new dependency for 3 texts
        hits = [p for s, _, p in sorted(scored, key=lambda t: (-t[0], t[1])) if s > 0][:2]
        out = "\n".join(f"{p['id']}: {p['text']}" for p in hits) or "No matching policy."
        log.info("tool search_policy(%r) -> %d hits", query, len(hits))
        return out

    @tool
    def request_refund(order_id: str, reason: str) -> str:
        """Refund an order if the shop's rules allow; refunds over $50 pause for a human reviewer."""
        # Rules 1-4 run again when the run resumes (the tool re-runs from here); they only read.
        o = orders.get(order_id)
        if o is None:
            return f"Order {order_id} not found."
        if order_id in shop["refunds"]:
            return f"{order_id} was already refunded."
        if o["status"] != "delivered":
            return f"Not eligible: {order_id} has not been delivered."
        days = (today - date.fromisoformat(o["delivered_on"])).days
        if days > REFUND_LIMIT_DAYS:
            return f"Not eligible: {order_id} was delivered {days} days ago (limit {REFUND_LIMIT_DAYS})."
        amount = o["amount"]
        if amount > APPROVAL_OVER:
            # Pauses: the caller gets this payload; on resume interrupt() returns the answer.
            answer = interrupt({"question": f"Approve refund of ${amount} for {order_id}?",
                                "order_id": order_id, "amount": amount, "reason": reason})
            log.info("tool request_refund(%s) reviewer answered %r", order_id, answer)
            if str(answer).strip().lower() != "yes":
                return f"Refund for {order_id} declined by reviewer."
            shop["refunds"].append(order_id)  # the only write, after the pause returns
            return f"Refunded {order_id} (${amount}) after approval."
        shop["refunds"].append(order_id)
        log.info("tool request_refund(%s) refunded $%s", order_id, amount)
        return f"Refunded {order_id} (${amount})."

    return [get_order, search_policy, request_refund]


def build_agent(llm, shop: dict, max_steps: int = 12):
    """Compile the agent loop (model <-> tools, ending in a Reply) with an in-memory checkpointer."""
    graph = create_agent(llm, tools=make_tools(shop), system_prompt=SYSTEM_PROMPT,
                         response_format=ToolStrategy(Reply), checkpointer=InMemorySaver())
    return graph.with_config({"recursion_limit": max_steps})


def make_llm():
    """Build the real model from the environment; fails loudly when no key is set."""
    import os

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set; tests and the grader use a scripted model instead")
    from langchain_openai import ChatOpenAI  # optional dependency, only for live runs

    return ChatOpenAI(model="gpt-4o-mini", temperature=0)
