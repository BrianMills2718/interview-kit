"""Order-support agent for a small shop (practice take-home).

A LangChain `create_agent` loop with three tools (get_order, search_policy, request_refund) over
the `shop` dict, a human-approval pause for refunds over $50, and a validated `Reply` as the
final answer. The grader calls `build_agent(llm, shop)`; see docs/MODEL.md for the diagrams.
"""

import logging
import re
from datetime import date
from typing import Literal, Optional, TypedDict

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from pydantic import BaseModel, Field, field_validator

log = logging.getLogger("order_support")

REFUND_WINDOW_DAYS = 30
APPROVAL_OVER = 50  # dollars; "over $50" read as strictly greater than 50
STEP_LIMIT = 25

SYSTEM_PROMPT = (
    "You are a support agent for a small shop. Use get_order for order facts, search_policy for "
    "policies, and request_refund to refund; never guess a fact a tool can give. Finish by "
    "calling Reply with the category, the order id (or null), one sentence describing the action "
    "taken, and the ids of the policies you relied on."
)


class Order(TypedDict):
    """One order as stored in data.json."""

    item: str
    amount: int
    status: str
    delivered_on: Optional[str]


class Policy(TypedDict):
    """One shop policy as stored in data.json."""

    id: str
    text: str


class Shop(TypedDict):
    """data.json plus the refunds list the grader adds."""

    today: str
    orders: dict[str, Order]
    policies: list[Policy]
    refunds: list[str]


class Reply(BaseModel):
    """The agent's final, validated answer to the customer."""

    category: Literal["refund", "shipping", "damaged", "other"]
    order_id: Optional[str] = Field(default=None, pattern=r"^A-\d{3}$",
                                    description="Order id in A-123 form, or null if none")
    action: str = Field(min_length=1, description="One sentence: what was done or will happen")
    policy_ids: list[str] = Field(default_factory=list, description="Ids like P-1 of the policies used")

    @field_validator("action")
    @classmethod
    def one_sentence(cls, v: str) -> str:
        """Reject an action that is more than one sentence, so the model retries."""
        # A sentence end followed by more text means a second sentence. Rejected alternative:
        # an LLM judge, too heavy for a schema check on a short field.
        if re.search(r"[.!?]\s+\S", v.strip()):
            raise ValueError("action must be one sentence")
        return v

    @field_validator("policy_ids")
    @classmethod
    def policy_id_form(cls, v: list[str]) -> list[str]:
        """Require each policy id in P-<n> form."""
        bad = [p for p in v if not re.fullmatch(r"P-\d+", p)]
        if bad:
            raise ValueError(f"policy ids must look like P-1, got {bad}")
        return v


def log_step(tool_name: str, args: dict, result: str) -> None:
    """Log one tool call (name, arguments, result size) so a run can be traced."""
    log.info("tool=%s args=%s result_chars=%d", tool_name, args, len(result))


def normalize_order_id(order_id: str) -> str:
    """Upper-case and trim an order id so 'a-101 ' finds A-101."""
    return order_id.strip().upper()


def format_order(order_id: str, order: Order) -> str:
    """Render one order line exactly as the task specifies; the date only once delivered."""
    line = f"{order_id}: {order['item']}, ${order['amount']}, {order['status']}"
    if order["status"] == "delivered" and order.get("delivered_on"):
        line += f" {order['delivered_on']}"
    return line


def days_since_delivery(order: Order, today: str) -> int:
    """Whole days between the delivery date and the shop's 'today'."""
    return (date.fromisoformat(today) - date.fromisoformat(order["delivered_on"])).days


STOPWORDS = {"the", "and", "for", "with", "can", "are", "you", "your", "our", "was", "has",
             "have", "not", "this", "that", "please", "order", "orders", "what", "when",
             "where", "how", "why", "did", "does", "will", "from", "about", "want", "would",
             "could", "need", "then", "within", "days"}


def stem(word: str) -> str:
    """Crude suffix strip so 'refunded', 'refunds' and 'refund' compare equal."""
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[: -len(suffix)]
            break
    if len(word) > 3 and word[-1] == word[-2]:  # shipp -> ship
        word = word[:-1]
    return word


def keywords(text: str) -> set[str]:
    """Distinct stemmed content words (3+ letters, not stopwords)."""
    return {stem(w) for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 3 and w not in STOPWORDS}


def score_policy(query: str, policy: Policy) -> int:
    """Number of distinct query keywords that appear in the policy text."""
    return len(keywords(query) & keywords(policy["text"]))


def refund_refusal(shop: Shop, order_id: str) -> Optional[str]:
    """Check refund rules 1-4 in the task's order; return the refusal text, or None if eligible."""
    order = shop["orders"].get(order_id)
    if order is None:
        return f"Order {order_id} not found."
    if order_id in shop["refunds"]:
        return f"{order_id} was already refunded."
    if order["status"] != "delivered" or not order.get("delivered_on"):
        return f"Not eligible: {order_id} has not been delivered."
    days = days_since_delivery(order, shop["today"])
    if days > REFUND_WINDOW_DAYS:
        return f"Not eligible: {order_id} was delivered {days} days ago (limit {REFUND_WINDOW_DAYS})."
    return None


def record_refund(shop: Shop, order_id: str) -> None:
    """The only write: append the order id to shop['refunds']."""
    shop["refunds"].append(order_id)
    log.info("refund recorded order=%s", order_id)


def make_tools(shop: Shop) -> list:
    """Build the three tools bound to this run's shop (no global state shared between runs)."""

    @tool
    def get_order(order_id: str) -> str:
        """Look up an order by id (e.g. 'A-101'). Returns 'A-101: item, $amount, status [delivery date]' or 'Order X not found.'"""
        oid = normalize_order_id(order_id)
        order = shop["orders"].get(oid)
        result = format_order(oid, order) if order else f"Order {oid} not found."
        log_step("get_order", {"order_id": order_id}, result)
        return result

    @tool
    def search_policy(query: str) -> str:
        """Find shop policies matching the query (refunds, shipping, damaged items). Returns up to 2 lines 'P-n: text', best first, or 'No matching policy.'"""
        scored = [(score_policy(query, p), i, p) for i, p in enumerate(shop["policies"])]
        # sort by score descending; ties keep the data order (index ascending)
        ranked = sorted((s for s in scored if s[0] > 0), key=lambda s: (-s[0], s[1]))[:2]
        result = "\n".join(f"{p['id']}: {p['text']}" for _, _, p in ranked) or "No matching policy."
        log_step("search_policy", {"query": query}, result)
        return result

    @tool
    def request_refund(order_id: str, reason: str) -> str:
        """Refund an order if the shop's rules allow it (delivered, within 30 days, not already refunded). Refunds over $50 wait for a human reviewer. Returns the outcome sentence."""
        oid = normalize_order_id(order_id)
        refusal = refund_refusal(shop, oid)
        if refusal:
            log_step("request_refund", {"order_id": order_id, "reason": reason}, refusal)
            return refusal
        amount = shop["orders"][oid]["amount"]
        if amount > APPROVAL_OVER:
            # On resume LangGraph re-runs this tool from the top, so nothing is written before
            # interrupt() returns. Rejected alternative: a separate approval node (more wiring).
            answer = interrupt({"question": f"Approve refund of ${amount} for {oid}?",
                                "order_id": oid, "amount": amount, "reason": reason})
            if str(answer).strip().lower() != "yes":
                result = f"Refund for {oid} declined by reviewer."
            else:
                record_refund(shop, oid)
                result = f"Refunded {oid} (${amount}) after approval."
        else:
            record_refund(shop, oid)
            result = f"Refunded {oid} (${amount})."
        log_step("request_refund", {"order_id": order_id, "reason": reason}, result)
        return result

    return [get_order, search_policy, request_refund]


def build_agent(llm, shop: Shop):
    """Compile the support agent: tools, validated Reply, in-memory checkpointer, step limit."""
    if "refunds" not in shop:
        raise ValueError("shop must include a 'refunds' list (the grader adds shop['refunds'] = [])")
    graph = create_agent(
        llm,
        tools=make_tools(shop),
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(Reply),  # invalid Reply -> error back to the model to retry
        checkpointer=InMemorySaver(),          # needed for interrupt() and resume
    )
    return graph.with_config({"recursion_limit": STEP_LIMIT})
