"""Reference solution. Do not open it during a practice run; it exists so tests can prove the grader passes and fails."""

import re
from datetime import date
from typing import Literal

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from pydantic import BaseModel, Field

APPROVAL_OVER = 50
REFUND_DAYS = 30


class Reply(BaseModel):
    """Final answer to the customer."""

    category: Literal["refund", "shipping", "damaged", "other"]
    order_id: str | None = Field(default=None, pattern=r"^[A-Z]-\d{3}$")
    action: str = Field(description="what was done, in one sentence")
    policy_ids: list[str] = Field(default_factory=list)


def build_agent(llm, shop):
    orders = shop["orders"]
    today = date.fromisoformat(shop["today"])

    @tool
    def get_order(order_id: str) -> str:
        """Look up one order by id, e.g. A-101."""
        o = orders.get(order_id)
        if not o:
            return f"Order {order_id} not found."
        when = f" {o['delivered_on']}" if o["delivered_on"] else ""
        return f"{order_id}: {o['item']}, ${o['amount']}, {o['status']}{when}"

    @tool
    def search_policy(query: str) -> str:
        """Find the policies most relevant to a question, best first."""
        words = {w for w in re.findall(r"[a-z]+", query.lower()) if len(w) >= 4}
        scored = [(sum(w in p["text"].lower() for w in words), p) for p in shop["policies"]]
        hits = [p for s, p in sorted(scored, key=lambda x: -x[0]) if s > 0][:2]
        return "\n".join(f"{p['id']}: {p['text']}" for p in hits) or "No matching policy."

    @tool
    def request_refund(order_id: str, reason: str) -> str:
        """Refund an order. Checks eligibility; large refunds wait for a human reviewer."""
        o = orders.get(order_id)
        if not o:
            return f"Order {order_id} not found."
        if order_id in shop["refunds"]:
            return f"{order_id} was already refunded."
        if o["status"] != "delivered":
            return f"Not eligible: {order_id} has not been delivered."
        age = (today - date.fromisoformat(o["delivered_on"])).days
        if age > REFUND_DAYS:
            return f"Not eligible: {order_id} was delivered {age} days ago (limit {REFUND_DAYS})."
        if o["amount"] > APPROVAL_OVER:
            answer = interrupt({"order_id": order_id, "amount": o["amount"], "reason": reason})
            if str(answer).strip().lower() != "yes":
                return f"Refund for {order_id} declined by reviewer."
            shop["refunds"].append(order_id)
            return f"Refunded {order_id} (${o['amount']}) after approval."
        shop["refunds"].append(order_id)
        return f"Refunded {order_id} (${o['amount']})."

    return create_agent(llm, tools=[get_order, search_policy, request_refund],
                        response_format=ToolStrategy(Reply), checkpointer=InMemorySaver(),
                        system_prompt="You are an order-support agent. Use the tools; never promise a refund the tool did not confirm. Cite policy ids.")
