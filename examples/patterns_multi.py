"""Two LangGraph patterns to copy: a supervisor that delegates to specialist agents, and streaming.

Supervisor: each specialist is a compiled graph wrapped as a tool. The supervisor is an ordinary
tool-calling agent, so it decides which specialist to ask, can ask several, and writes the final
answer. This is the "subagents as tools" pattern: no extra package needed (rejected alternative:
the separate langgraph-supervisor add-on, one more dependency with its own API to learn).

Streaming: graph.stream(..., stream_mode="updates") yields {node_name: update} after each step,
which is how a UI or a log shows progress while the agent works.

Checked against langgraph 1.2.14 / langchain-core 1.6.9 (Pregel.stream docs, context7, 2026-10-11).
Test: pytest -v tests/test_patterns_multi.py (offline, scripted fake models).
"""

import logging
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

log = logging.getLogger("patterns_multi")


class State(TypedDict):
    """Graph state: the running conversation."""

    messages: Annotated[list[AnyMessage], add_messages]


def specialist_tool(name: str, description: str, graph) -> StructuredTool:
    """Wrap a compiled specialist graph as a tool the supervisor can call with a question."""

    def ask_specialist(question: str) -> str:
        result = graph.invoke({"messages": [("user", question)]}, config={"recursion_limit": 10})
        answer = result["messages"][-1].content
        log.info("specialist %s: %d chars", name, len(answer))
        return answer

    # The description is the prompt the supervisor sees when choosing: say what this one knows.
    return StructuredTool.from_function(ask_specialist, name=f"ask_{name}", description=description)


def build_supervisor(llm, specialists: list[StructuredTool], system: str):
    """Supervisor agent: calls specialist tools in a loop until it answers without a tool call."""
    llm_with_tools = llm.bind_tools(specialists)

    def supervisor(state: State) -> dict:
        reply = llm_with_tools.invoke([SystemMessage(system), *state["messages"]])
        log.info("supervisor: tool_calls=%s", [c["name"] for c in getattr(reply, "tool_calls", [])])
        return {"messages": [reply]}

    g = StateGraph(State)
    g.add_node("supervisor", supervisor)
    g.add_node("specialists", ToolNode(specialists, handle_tool_errors=True))
    g.add_edge(START, "supervisor")
    g.add_conditional_edges("supervisor", tools_condition, {"tools": "specialists", "__end__": "__end__"})
    g.add_edge("specialists", "supervisor")
    return g.compile()


def stream_steps(graph, question: str):
    """Yield (node, short description) after each step, for progress display or a trace log."""
    for update in graph.stream({"messages": [("user", question)]}, config={"recursion_limit": 10},
                               stream_mode="updates"):
        for node, change in update.items():
            msg = change["messages"][-1]
            calls = [c["name"] for c in getattr(msg, "tool_calls", [])]
            yield node, f"calls {calls}" if calls else str(msg.content)[:80]
