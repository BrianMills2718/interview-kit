"""Minimal tool-calling agent in LangGraph: a template to copy and adapt.

Run live:   OPENAI_API_KEY=... python examples/agent_template.py "Where is order A-100?"
Test:       pytest -v   (offline, uses a scripted fake model)
"""

import logging
import sys
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

log = logging.getLogger("agent")

ORDERS = {"A-100": "shipped", "A-101": "processing"}  # stand-in for a real data source


class State(TypedDict):
    """Graph state: the running conversation. add_messages appends instead of replacing."""

    messages: Annotated[list[AnyMessage], add_messages]


@tool
def lookup_order(order_id: str) -> str:
    """Return the status of an order given its ID, e.g. 'A-100'."""
    if order_id not in ORDERS:
        raise ValueError(f"Unknown order id {order_id!r}; known ids look like 'A-100'.")
    return f"Order {order_id}: {ORDERS[order_id]}"


TOOLS = [lookup_order]
SYSTEM = "You are a support agent. Use tools for facts; never guess. Say so if you cannot find it."


def build_graph(llm):
    """Wire agent <-> tools in a loop that ends when the model stops calling tools."""
    llm_with_tools = llm.bind_tools(TOOLS)

    def agent(state: State) -> dict:
        reply = llm_with_tools.invoke([SystemMessage(SYSTEM), *state["messages"]])
        log.info("agent: tool_calls=%s", [c["name"] for c in getattr(reply, "tool_calls", [])])
        return {"messages": [reply]}

    g = StateGraph(State)
    g.add_node("agent", agent)
    # handle_tool_errors returns the error text to the model so it can recover, instead of crashing
    g.add_node("tools", ToolNode(TOOLS, handle_tool_errors=True))
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition)
    g.add_edge("tools", "agent")
    return g.compile()


def ask(graph, question: str) -> str:
    """Run one question through the graph with a bounded number of steps."""
    result = graph.invoke({"messages": [("user", question)]}, config={"recursion_limit": 10})
    return result["messages"][-1].content


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    import os

    from langchain_openai import ChatOpenAI  # swap for any chat model with tool calling

    if os.environ.get("OPENROUTER_API_KEY"):  # same OpenAI-style API, different endpoint
        llm = ChatOpenAI(model="openai/gpt-4o-mini", base_url="https://openrouter.ai/api/v1",
                         api_key=os.environ["OPENROUTER_API_KEY"])
    else:
        llm = ChatOpenAI(model="gpt-4o-mini")
    print(ask(build_graph(llm), " ".join(sys.argv[1:]) or "Where is order A-100?"))
