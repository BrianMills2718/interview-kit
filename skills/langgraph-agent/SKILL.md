---
name: langgraph-agent
description: Build a tool-calling agent or multi-step graph with LangGraph (state, tools, routing, memory, limits). Use when the task is an agent that uses tools or takes steps.
---

# Skill: build a tool-calling agent with LangGraph

Use when the task is "build an agent that uses tools / takes steps / answers from data".
Tested with langgraph 1.2.14, langchain 1.4.4, langchain-core 1.6.9. Runnable versions:
`examples/agent_template.py` (hand-built graph) and `examples/patterns.py` (structured output,
retrieval tool, human approval), each with offline tests in `tests/`.

## Shape

```
START -> agent --(model asked for tools?)--> tools -> agent ... -> END
```

## Core code

```python
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]  # add_messages appends, not replaces


@tool
def lookup_order(order_id: str) -> str:
    """Return the status of an order given its ID, e.g. 'A-100'."""
    ...


TOOLS = [lookup_order]


def build_graph(llm):
    llm_with_tools = llm.bind_tools(TOOLS)

    def agent(state: State) -> dict:
        system = SystemMessage("You are a support agent. Use tools for facts; never guess.")
        return {"messages": [llm_with_tools.invoke([system, *state["messages"]])]}

    g = StateGraph(State)
    g.add_node("agent", agent)
    g.add_node("tools", ToolNode(TOOLS))
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition)  # -> "tools" or END
    g.add_edge("tools", "agent")
    return g.compile()


graph = build_graph(llm)
result = graph.invoke({"messages": [("user", "Where is order A-100?")]},
                      config={"recursion_limit": 10})
print(result["messages"][-1].content)
```

## Variations

- **Prebuilt shortcut:** `from langchain.agents import create_agent`;
  `create_agent(llm, tools=TOOLS, system_prompt="...")`. Fine for a first version; hand-built graph
  when custom routing or extra state is needed. Say which and why.
- **Memory across turns:** `graph = g.compile(checkpointer=InMemorySaver())` from
  `langgraph.checkpoint.memory`, then pass `config={"configurable": {"thread_id": "1"}}`.
- **Structured final answer:** `create_agent(llm, tools, response_format=ToolStrategy(Answer))`
  (`from langchain.agents.structured_output import ToolStrategy`); invalid output is sent back to
  the model to retry, and the result is in `out["structured_response"]`. In a hand-built graph, a
  last node calling `llm.with_structured_output(Answer)`. See `examples/patterns.py`.
- **Retrieval:** a tool returning the top passages as `id: text`, and a clear "No matching
  documents." when nothing matches. See `search_docs` in `examples/patterns.py`.
- **Extra state:** add fields to `State` (e.g. `attempts: int`) and a router function for
  `add_conditional_edges` that returns a node name.
- **Human approval:** `interrupt(payload)` inside a node pauses the run (the caller sees
  `result["__interrupt__"]`); resume with `graph.invoke(Command(resume="yes"), cfg)` on the same
  `thread_id`. Needs a checkpointer. See `build_refund_graph` in `examples/patterns.py`.
- **Retries:** a router that sends to a `check` node, which loops back to
  `agent` with feedback or ends, with a counter so it cannot loop forever.

## Current API watchlist (the IDE's AI may suggest the old form)

Checked 2026-10-11 against the installed packages (`pip show langchain langgraph`). If the
installed versions differ, re-check before trusting this table or the assistant.

| Old form the AI may write | Current form | Checked in |
|---|---|---|
| `from langgraph.prebuilt import create_react_agent` | `from langchain.agents import create_agent` (still imports; calling it warns `LangGraphDeprecatedSinceV10`) | langgraph 1.2.14 / langchain 1.4.4 |
| `create_react_agent(llm, tools, prompt=...)`; `state_modifier=` (no longer exists anywhere in `langgraph.prebuilt`) | `create_agent(llm, tools=..., system_prompt="...")` | langgraph 1.2.14 / langchain 1.4.4 |
| `from langchain.chains import ...`, `from langchain import hub` | removed: `No module named 'langchain.chains'` / `'langchain.hub'`; write the graph or prompt yourself | langchain 1.4.4 |
| `langgraph_supervisor.create_supervisor`, swarm add-ons | not installed with langgraph; wrap each subagent as a `@tool` the supervisor calls | langgraph 1.2.14 |
| "recursion_limit defaults to 25" | default is 10007 (env `LANGGRAPH_DEFAULT_RECURSION_LIMIT`): a looping model runs a long time; always pass `config={"recursion_limit": 10}` | langgraph 1.2.14 |
| `GenericFakeChatModel(...).bind_tools(tools)` in tests | raises `NotImplementedError`; subclass with `def bind_tools(self, tools, **kw): return self` (see tests) | langchain-core 1.6.9 |
| `llm.with_structured_output` inside `create_agent` | `response_format=ToolStrategy(Model)`; result in `out["structured_response"]` | langchain 1.4.4 |
| `from langchain.mcp import ...` on a plain install | needs `pip install "langchain[mcp]"` (imports `fastmcp`) | langchain 1.4.4 |

## Pitfalls

- Forgetting `add_messages`: each node then overwrites the history.
- No `recursion_limit`: the default is 10007 steps, so a confused model loops (and bills) for a long time.
- Tool docstrings that are vague: the model picks the wrong tool or wrong arguments.
- Testing only against the live model: flaky and slow. Use a fake model (see the test).

## Several agents: a supervisor with specialists as tools

Tested in `examples/patterns_multi.py` (`tests/test_patterns_multi.py`). Wrap each specialist's
compiled graph as a tool; the supervisor is the same agent loop as above, with those tools.

```python
def specialist_tool(name, description, graph):
    def ask_specialist(question: str) -> str:
        out = graph.invoke({"messages": [("user", question)]}, config={"recursion_limit": 10})
        return out["messages"][-1].content
    return StructuredTool.from_function(ask_specialist, name=f"ask_{name}", description=description)
```

The description is what the supervisor reads when it chooses, so say what each specialist
knows. No extra package is needed; the separate `langgraph-supervisor` add-on is one more API.

## Streaming progress

`graph.stream(inputs, config, stream_mode="updates")` yields `{node_name: update}` after each
step (`"values"` yields the whole state; `"messages"` yields `(token_chunk, metadata)` pairs
from the model). `stream_steps()` in `examples/patterns_multi.py` turns updates into
`("agent", "calls ['lookup_order']")`, `("tools", "Order A-100: shipped")`, ... for a log or UI.
