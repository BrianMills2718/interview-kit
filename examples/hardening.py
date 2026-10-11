"""Production hardening for a LangChain agent: retries, call limits, cost tracking, guardrails.

Every piece is LangChain's own (langchain 1.4, langchain-core 1.6), added as middleware to
create_agent; nothing here is hand-written retry or regex-on-output logic.

Run live:  OPENAI_API_KEY=... python examples/hardening.py "Where is order A-100? I'm a@b.com"
Test:      pytest tests/test_hardening.py -v   (offline, scripted fake models)
"""

import logging
import sys

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ModelRetryMiddleware,
    PIIMiddleware,
    ToolCallLimitMiddleware,
    before_agent,
)
from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.messages import AIMessage
from langchain_core.tools import tool

log = logging.getLogger("hardening")

ORDERS = {"A-100": "shipped", "A-101": "processing"}
PRICE_PER_1K = {"input": 0.00015, "output": 0.0006}  # USD; set from the provider's price page
MAX_INPUT_CHARS = 2000


@tool
def lookup_order(order_id: str) -> str:
    """Look up an order's shipping status by order ID, e.g. 'A-100'."""
    if order_id not in ORDERS:
        raise ValueError(f"Unknown order id {order_id!r}; known ids look like 'A-100'.")
    return f"Order {order_id}: {ORDERS[order_id]}"


@before_agent(can_jump_to=["end"])
def reject_oversized_input(state, runtime):
    """Guardrail: refuse an over-long request before any model call is spent on it."""
    text = state["messages"][-1].content
    if len(text) > MAX_INPUT_CHARS:
        log.warning("rejected input of %d chars", len(text))
        return {
            "messages": [AIMessage(f"Request too long ({len(text)} chars, max {MAX_INPUT_CHARS}).")],
            "jump_to": "end",
        }
    return None


def build_agent(llm, initial_delay: float = 1.0):
    """Agent with retries on transient model errors, hard call limits and input guardrails."""
    return create_agent(
        llm,
        tools=[lookup_order],
        system_prompt="You are a support agent. Use tools for facts; never guess.",
        middleware=[
            reject_oversized_input,
            PIIMiddleware("email", strategy="redact", apply_to_input=True),  # model never sees it
            ModelRetryMiddleware(max_retries=2, initial_delay=initial_delay, on_failure="error"),
            ModelCallLimitMiddleware(run_limit=6, exit_behavior="end"),  # stops a runaway loop
            ToolCallLimitMiddleware(run_limit=5, exit_behavior="continue"),
        ],
    )


def ask_with_cost(agent, question: str) -> tuple[str, dict]:
    """Run one question; return (answer, usage) where usage has tokens and estimated USD."""
    with get_usage_metadata_callback() as cb:
        out = agent.invoke({"messages": [("user", question)]})
    tokens_in = sum(u.get("input_tokens", 0) for u in cb.usage_metadata.values())
    tokens_out = sum(u.get("output_tokens", 0) for u in cb.usage_metadata.values())
    usd = tokens_in / 1000 * PRICE_PER_1K["input"] + tokens_out / 1000 * PRICE_PER_1K["output"]
    usage = {"input_tokens": tokens_in, "output_tokens": tokens_out, "usd": round(usd, 6)}
    log.info("usage %s", usage)
    return out["messages"][-1].content, usage


if __name__ == "__main__":
    from langchain_openai import ChatOpenAI

    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    answer, usage = ask_with_cost(build_agent(ChatOpenAI(model="gpt-5-mini")), " ".join(sys.argv[1:]))
    print(answer, usage, sep="\n")
