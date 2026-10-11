"""Three tested LangGraph/LangChain patterns to copy: structured output, a retrieval tool,
and a human approval step. Checked against langchain 1.4.4, langgraph 1.2.14.

Test: pytest -v tests/test_patterns.py   (offline, scripted fake model)
"""

import re
from typing import Annotated, TypedDict

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import AnyMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field

# --- 1. Structured output -------------------------------------------------------------
# create_agent(response_format=ToolStrategy(Model)) offers the schema to the model as a tool.
# If the model's arguments fail Pydantic validation, the error goes back to the model and it
# retries; the validated object is in result["structured_response"].


class OrderAnswer(BaseModel):
    """Final answer about one order."""

    order_id: str = Field(pattern=r"^[A-Z]-\d{3}$")
    status: str = Field(pattern="^(shipped|processing|unknown)$")
    source: str = Field(description="id of the document the status came from")


def build_structured_agent(llm, tools=()):
    """Agent whose final output is a validated OrderAnswer."""
    return create_agent(llm, tools=list(tools), response_format=ToolStrategy(OrderAnswer),
                        system_prompt="Answer from tool results only. Cite the document id.")


# --- 2. Retrieval tool ------------------------------------------------------------------
# Retrieval is just a tool that returns the best-matching passages with their ids. Keyword
# overlap keeps this offline; swap score() for embeddings without changing the tool's contract.

DOCS = {
    "kb-1": "Refunds are allowed within 30 days of delivery for unused items.",
    "kb-2": "Orders ship within 2 business days; express ships the same day.",
    "kb-3": "Damaged items can be returned at any time with a photo of the damage.",
}


def score(query: str, text: str) -> int:
    """Number of distinct query words (3+ letters) that appear in the text."""
    words = {w for w in re.findall(r"[a-z]+", query.lower()) if len(w) >= 3}
    return len(words & set(re.findall(r"[a-z]+", text.lower())))


@tool
def search_docs(query: str, k: int = 2) -> str:
    """Search the help-center documents. Returns up to k passages as 'id: text', best first."""
    ranked = sorted(DOCS.items(), key=lambda kv: score(query, kv[1]), reverse=True)
    hits = [f"{i}: {t}" for i, t in ranked[:k] if score(query, t) > 0]
    if not hits:
        return "No matching documents."  # an explicit empty result, not an empty string
    return "\n".join(hits)


# --- 3. Human approval (interrupt) -------------------------------------------------------
# interrupt() pauses the graph and returns its payload to the caller under "__interrupt__".
# The caller resumes with Command(resume=value) on the same thread_id. Needs a checkpointer.

REFUNDS_ISSUED: list[str] = []  # stand-in for a real side effect


class RefundState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    order_id: str
    approved: bool


def ask_approval(state: RefundState) -> dict:
    """Pause and ask a human to approve the refund; resume value 'yes' approves."""
    answer = interrupt({"question": f"Refund order {state['order_id']}?"})
    return {"approved": str(answer).strip().lower() == "yes"}


def issue_refund(state: RefundState) -> dict:
    """The irreversible action: only reached after approval."""
    REFUNDS_ISSUED.append(state["order_id"])
    return {"messages": [("assistant", f"Refund issued for {state['order_id']}.")]}


def decline(state: RefundState) -> dict:
    return {"messages": [("assistant", f"Refund for {state['order_id']} was not approved.")]}


def build_refund_graph():
    """approve? -> issue_refund | decline. Compiled with an in-memory checkpointer."""
    g = StateGraph(RefundState)
    g.add_node("ask_approval", ask_approval)
    g.add_node("issue_refund", issue_refund)
    g.add_node("decline", decline)
    g.add_edge(START, "ask_approval")
    g.add_conditional_edges("ask_approval", lambda s: "issue_refund" if s["approved"] else "decline")
    g.add_edge("issue_refund", END)
    g.add_edge("decline", END)
    return g.compile(checkpointer=InMemorySaver())


def run_refund(graph, order_id: str, human_answer: str, thread: str = "t1"):
    """Start the refund flow, show the pause, then resume with the human's answer."""
    cfg = {"configurable": {"thread_id": thread}}
    paused = graph.invoke({"messages": [], "order_id": order_id, "approved": False}, cfg)
    final = graph.invoke(Command(resume=human_answer), cfg)
    return paused, final
