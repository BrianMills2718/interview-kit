"""Order-support agent: three tools over a shop dict, human approval for big refunds, validated Reply."""

import logging
import re
from datetime import date
from typing import Literal, Optional

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from pydantic import BaseModel, Field

log = logging.getLogger("solution")

APPROVAL_LIMIT = 50  # refunds strictly over this need a reviewer (PROBLEM.md rule 5)
REFUND_WINDOW_DAYS = 30

SYSTEM_PROMPT = (
    "You are a support agent for a small shop. Use get_order for order facts, search_policy for "
    "rules, and request_refund to refund; never guess. Finish by calling Reply."
)


class Reply(BaseModel):
    """Final validated answer to the customer message."""

    category: Literal["refund", "shipping", "damaged", "other"]
    order_id: Optional[str] = Field(default=None, pattern=r"^A-\d{3}$", description="A-123 form, or null")
    action: str = Field(description="one sentence saying what was done")
    policy_ids: list[str] = Field(default_factory=list, description="ids like P-1 of policies used")


def _words(text: str) -> set[str]:
    """Lower-case words of 3+ letters; the unit of keyword overlap."""
    return {w for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 3}


def make_tools(shop: dict) -> list:
    """Build the three tools as closures over shop, so each graph sees only its own data."""
    orders, today = shop["orders"], date.fromisoformat(shop["today"])

    @tool
    def get_order(order_id: str) -> str:
        """Look up an order by id like 'A-101'. Returns item, amount, status and delivery date."""
        o = orders.get(order_id)
        if o is None:
            return f"Order {order_id} not found."
        line = f"{order_id}: {o['item']}, ${o['amount']}, {o['status']}"
        return f"{line} {o['delivered_on']}" if o["status"] == "delivered" else line

    @tool
    def search_policy(query: str) -> str:
        """Find shop policies matching a query, best first, at most 2, as 'P-1: text' lines."""
        q = _words(query)
        # rejected: embeddings; keyword overlap is offline, deterministic and enough for 3 policies
        scored = [(len(q & _words(p["text"])), i, p) for i, p in enumerate(shop["policies"])]
        hits = sorted((s for s in scored if s[0] > 0), key=lambda s: (-s[0], s[1]))[:2]
        if not hits:
            return "No matching policy."
        return "\n".join(f"{p['id']}: {p['text']}" for _, _, p in hits)

    @tool
    def request_refund(order_id: str, reason: str) -> str:
        """Refund an order if the rules allow; refunds over $50 pause for a human reviewer."""
        o = orders.get(order_id)
        if o is None:
            return f"Order {order_id} not found."
        if order_id in shop["refunds"]:
            return f"{order_id} was already refunded."
        if o["status"] != "delivered":
            return f"Not eligible: {order_id} has not been delivered."
        days = (today - date.fromisoformat(o["delivered_on"])).days
        if days > REFUND_WINDOW_DAYS:
            return f"Not eligible: {order_id} was delivered {days} days ago (limit {REFUND_WINDOW_DAYS})."
        amount = o["amount"]
        if amount > APPROVAL_LIMIT:
            # interrupt() re-runs this tool from the top on resume, so the write happens only after it
            answer = interrupt({"question": f"Approve refund of {order_id} (${amount})? Reason: {reason}"})
            log.info("reviewer answered %r for %s", answer, order_id)
            if str(answer).strip().lower() != "yes":
                return f"Refund for {order_id} declined by reviewer."
            shop["refunds"].append(order_id)
            return f"Refunded {order_id} (${amount}) after approval."
        shop["refunds"].append(order_id)
        return f"Refunded {order_id} (${amount})."

    return [get_order, search_policy, request_refund]


def build_agent(llm, shop: dict):
    """Compile the agent graph: tool loop, Reply as structured output (retried if invalid), checkpointer."""
    # rejected: a hand-built StateGraph; create_agent already gives the loop, Reply retry and interrupts
    return create_agent(
        llm,
        tools=make_tools(shop),
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(Reply),  # invalid args -> error message back to the model to retry
        checkpointer=InMemorySaver(),
    )

