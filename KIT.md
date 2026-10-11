# Interview kit (combined; source: github.com/BrianMills2718/interview-kit)

<!-- AGENTS.md -->
# Working rules for the coding assistant

These rules apply to any AI coding assistant working in this project. Read them before acting.

## How we work

1. **Plan before code.** Restate the task in 3-5 lines, list assumptions, and propose a short
   numbered plan. Wait for approval before editing files.
2. **One small step at a time.** Each edit does one thing that can be run and checked. No
   multi-file rewrites in one go.
3. **Run it after every change.** Execute the code or the tests after each edit and report the
   actual output. Never say "this should work" without running it.
4. **Tests define done.** Write a small test for each behavior before or with the code. Include
   at least one case where a trivial or wrong implementation would fail.
5. **Fail loudly.** No bare `except:`, no silent fallbacks that hide errors. Raise or log with
   context. A missing API key or bad input is an error message, not an empty result.
6. **Keep it simple.** Standard library and the libraries already in use first. No new
   dependency or abstraction without a stated reason.
7. **Explain as you go.** Every function has a one-line docstring saying what it does and why.
   Non-obvious decisions get a short comment naming the alternative that was rejected.
8. **Say when unsure.** If the spec is ambiguous, state the interpretation chosen and why,
   in the code and in the README, rather than guessing silently.

## Agentic AI specifics

- Typed state and typed outputs: `TypedDict` for graph state, Pydantic models for structured
  LLM output (`llm.with_structured_output(Model)`), validated, never parsed with regex.
- Tools have precise names, docstrings and typed arguments: the docstring *is* the prompt the
  model sees. Tools return short, structured strings or dicts and raise clear errors.
- Bound every loop: a maximum number of steps (`recursion_limit`) and an explicit stop condition.
- Keep the LLM swappable: one function builds the model; tests use a fake model so they run
  offline and deterministically.
- Log each step (node name, tool called, arguments, result size) so a run can be traced.
- Evaluate with a handful of concrete cases with known answers, including a failure case;
  report pass/fail per case, not a single score.

## Final deliverable checklist

- [ ] Runs end to end from one command shown in the README.
- [ ] Tests pass; the README shows the command and the result.
- [ ] README: approach, design decisions and rejected alternatives, assumptions, limitations,
      what I would do next with more time.
- [ ] Places where the AI's suggestion was wrong or changed, and why, are noted.

<!-- skills/evaluate-agent.md -->
# Skill: test and evaluate an agent

Use when the solution includes an LLM or agent and needs to show it works.

## Two layers

1. **Deterministic tests (pytest, offline).** Replace the model with a fake that returns
   scripted messages, so the graph logic, tool routing and error handling are tested exactly:

   ```python
   from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
   from langchain_core.messages import AIMessage

   class FakeToolModel(GenericFakeChatModel):
       def bind_tools(self, tools, **kwargs):
           return self  # tools are ignored; replies are scripted

   llm = FakeToolModel(messages=iter([
       AIMessage("", tool_calls=[{"name": "lookup_order", "args": {"order_id": "A-100"}, "id": "1"}]),
       AIMessage("Order A-100 has shipped."),
   ]))
   ```

   Assert on membership, not counts: the right tool was called with the right arguments, and
   the final answer contains the fact the tool returned.

2. **Live evaluation (a small table).** 5-10 questions with known answers, including:
   one needing no tool, one needing two tools, one with bad input, one the agent should refuse
   or say "I don't know". Print a table: question, expected, got, pass/fail, tools used.

## Reading results

- For each failure, look at the full message trace (every tool call, its arguments, what came
  back), then classify: the tool never returned the needed fact, it returned it but the model
  ignored it, or the expected answer was wrong.
- Report pass/fail per case and the trace finding, not just an accuracy number.

<!-- skills/explain-your-work.md -->
# Skill: explain the solution

Use at the end, and keep it updated while working. Reviewers read this first.

## README template

```markdown
# <Task name>

## Run it
<one command>  ->  <what you should see>
Tests: `pytest -v`  ->  N passed

## Approach
Two or three sentences: what the system does and the shape of the solution (a diagram line
like START -> agent -> tools -> agent -> END helps).

## Design decisions
| Decision | Why | Rejected alternative |
|---|---|---|

## Assumptions
Where the spec was ambiguous and which reading I chose.

## How I used the AI assistant
- What I delegated (boilerplate, test cases, API lookups) and what I kept (design, review).
- Where its suggestion was wrong or I changed it, and how I caught it (a failing test, a run).

## Limitations and next steps
What breaks, what is untested, and what I would do with more time.
```

## In the code

- Module docstring at the top: what this file is for.
- One-line docstring per function; comments only for non-obvious "why".

<!-- skills/langgraph-agent.md -->
# Skill: build a tool-calling agent with LangGraph

Use when the task is "build an agent that uses tools / takes steps / answers from data".
Tested with langgraph 1.2, langchain-core 1.6. A runnable version is in
`examples/agent_template.py`.

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

- **Prebuilt shortcut:** `from langchain.agents import create_agent` (LangChain 1.x) or the older
  `langgraph.prebuilt.create_react_agent(llm, TOOLS)`. Fine for a first version; hand-built graph
  when custom routing or extra state is needed. Say which and why.
- **Memory across turns:** `graph = g.compile(checkpointer=InMemorySaver())` from
  `langgraph.checkpoint.memory`, then pass `config={"configurable": {"thread_id": "1"}}`.
- **Structured final answer:** a last node calling `llm.with_structured_output(Answer)` where
  `Answer` is a Pydantic model.
- **Extra state:** add fields to `State` (e.g. `attempts: int`) and a router function for
  `add_conditional_edges` that returns a node name.
- **Human in the loop / retries:** a router that sends to a `check` node, which loops back to
  `agent` with feedback or ends, with a counter so it cannot loop forever.

## Pitfalls

- Forgetting `add_messages`: each node then overwrites the history.
- No `recursion_limit`: a confused model loops until the default limit error.
- Tool docstrings that are vague: the model picks the wrong tool or wrong arguments.
- Testing only against the live model: flaky and slow. Use a fake model (see the test).
