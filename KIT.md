# Interview kit (combined; source: the interview-kit repo)

<!-- AGENTS.md -->
# Working rules for the coding assistant

These rules apply to any AI coding assistant working in this project. Read them before acting.

## How we work

1. **Plan before code.** Write `PLAN.md` from `PLAN.template.md` (see `skills/plan/SKILL.md`):
   goal with the quoted requirements, checkable done-when items, small steps, a one-page
   system model (or one line saying why none is needed), assumptions. How to think at each
   stage (design chain, model, views, decisions) is in `kit/method/README.md`.
   Wait for approval before editing code (the person types "plan approved" in the chat, so the
   recording shows it).
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

## Roles (subagents)

Work in four roles, one at a time, each described in `agents/`: **planner** writes `PLAN.md`,
**implementer** does one step and runs it, **tester** writes tests that could fail, **reviewer**
critiques the result against the plan before anything is called done. When asked to act as a
role, follow that file.

## Enforcement

`bash kit/check.sh` checks the plan is concrete, the code compiles and the tests pass, and prints
counts. `bash kit/check.sh --final` also requires every done-when item ticked and the README
sections present. Run it after each step; the work is done only when `--final` passes.

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

<!-- PLAN.template.md -->
# Plan

## Goal
<2-3 sentences in my words, plus the exact requirement lines quoted from the prompt>

## Done when
- [ ] `<command>` -> `<expected result>`
- [ ] `pytest -v` -> all tests PASSED, none skipped
- [ ] README explains approach, decisions, AI use and limitations

## Steps
1. <smallest runnable step>
2. ...

## System model
<one page per kit/method/system-model.md (goals, context, parts, runtime with the writing function, quality checks, unknowns), or one line: System model: not needed, because REASON>

## Assumptions
- <ambiguity> -> <reading chosen, and why>

## Risks
- <what could make this wrong> -> <how it would show>

<!-- skills/evaluate-agent/SKILL.md -->
---
name: evaluate-agent
description: Test an agent offline with a scripted fake model and evaluate it on known cases with per-case pass/fail and trace reading. Use whenever a solution includes an LLM or agent.
---

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

<!-- skills/explain-your-work/SKILL.md -->
---
name: explain-your-work
description: Write the README and in-code explanations reviewers read first, including how the AI assistant was used. Use at the end and keep updated while working.
---

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

<!-- skills/langgraph-agent/SKILL.md -->
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
  `thread_id`. Needs a checkpointer. See `build_refund_graph` in `examples/patterns.py`. Inside a
  `@tool` of `create_agent` it also works (pass `checkpointer=`); see the watchlist for the re-run.
- **Retries:** a router that sends to a `check` node, which loops back to
  `agent` with feedback or ends, with a counter so it cannot loop forever.

## Current API watchlist (the IDE's AI may suggest the old form)

Checked 2026-10-11 against the installed packages (`python -c "import importlib.metadata as m; print(m.version('langchain'), m.version('langgraph'))"`; `pip show` fails inside a uv venv). If the
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
| `Command(resume=None)` to mean "no answer" | crashes (`UnboundLocalError`); resume with a real value, e.g. `"no"` | langgraph 1.2.14 |
| `interrupt()` inside a `@tool` used by `create_agent` | works, but on resume the whole tool runs again from the top: do side effects (refund, write) only after `interrupt()` returns | langgraph 1.2.14 |

The model provider: the task names it (or gives a key). Install that provider's package
(`langchain-openai`, `langchain-anthropic`, ...), read the key from the environment variable it
names, and fail with a clear message when it is missing. Tests use the fake model, so they need no key.

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

<!-- skills/mcp-and-a2a/SKILL.md -->
---
name: mcp-and-a2a
description: What MCP (agent-to-tool) and A2A (agent-to-agent) are, when to use each, and a tested MCP server. Use when a task mentions tools over a protocol, tool servers, or agents talking to agents.
---

# Skill: MCP and A2A in one page

Checked 2026-10-11 against the MCP spec 2026-07-28 (modelcontextprotocol.io/specification),
the `mcp` Python SDK 2.3.0, and the A2A spec 1.0.0 (a2a-protocol.org/latest/specification).

## Which one

| | MCP (Model Context Protocol) | A2A (Agent2Agent) |
|---|---|---|
| Connects | an AI app to **tools and data** | an agent to **another agent** |
| The other side is | a server exposing functions | an opaque agent doing a task |
| Use when | the model needs to call a function or read a resource | work is handed to an agent you do not control |

In a take-home, plain LangChain `@tool` functions are usually enough. Use MCP if the task asks
for it or the tools must be shared across apps; mention A2A as the next step, not the core.

## MCP: the facts that matter

- JSON-RPC 2.0 messages. Roles: **host** (the app), **client** (one connector per server),
  **server**.
- Servers offer **tools** (functions the model calls), **resources** (data to read) and
  **prompts** (templates). Clients may offer **elicitation** (asking the user for input).
- Standard transports: **stdio** (client launches the server as a subprocess) and **Streamable
  HTTP** (one HTTP endpoint; replies as JSON or an SSE stream).
- Security: tools are arbitrary code; the host must get user consent before calling one, and
  tool descriptions from an untrusted server are untrusted input.

Tested server (`examples/mcp_server.py`, `tests/test_mcp_server.py`):

```python
from mcp.server import MCPServer                     # mcp 2.x; 1.x called it FastMCP
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("orders")

@mcp.tool()
def lookup_order(order_id: str) -> str:
    """Return the status of an order given its ID, e.g. 'A-100'."""   # the model reads this
    if order_id not in ORDERS:
        raise ToolError(f"Unknown order id {order_id!r}")   # message reaches the model
    return f"Order {order_id}: {ORDERS[order_id]}"
```

- Raise `ToolError` for expected failures: any other exception reaches the client only as
  `Error executing tool lookup_order` (found by the test, not in most tutorials).
- Test without a network: `async with mcp.Client(server) as c: await c.call_tool(...)`;
  results use `is_error` and `input_schema` (snake_case in 2.x).
- Into LangGraph: the `langchain-mcp-adapters` package (`MultiServerMCPClient`, then
  `await client.get_tools()`) turns server tools into LangChain tools. Untested here: check
  the installed version's docs before using it.

## A2A: the facts that matter

- An agent publishes an **Agent Card** (JSON: identity, skills, endpoint, auth) at
  `https://{domain}/.well-known/agent-card.json`.
- Work is a **Task** with states such as submitted, working, input-required, completed,
  failed. **Messages** (role user or agent) carry **Parts** (text, file, data); results come
  back as **Artifacts**.
- Bindings: JSON-RPC (`SendMessage`, `SendStreamingMessage`), gRPC, and HTTP+JSON. Streaming
  uses Server-Sent Events.
- Python SDK: `a2a-sdk`. Untested here.

## Say this in the README

Name which protocol you used and why, what you would expose over MCP or A2A with more time,
and the security point: tool servers run code, so calls need consent and tool text is untrusted.

<!-- skills/plan/SKILL.md -->
---
name: plan
description: Write a short PLAN.md before any code - the goal, checkable done-when items, numbered steps and risks - and keep it current. Use at the start of every task and whenever scope changes.
---

# Skill: plan before code

A plan is one short file, `PLAN.md`, written before the first code edit and updated as work
goes. It is the contract the checks in `check.sh` hold the work to. Copy `PLAN.template.md`.

## What goes in it

1. **Goal**: the task in your own words, 2-3 sentences. Quote the exact requirement lines
   from the prompt you were given.
2. **Done when**: checkable items, each one a command or an observable result, e.g.
   "`pytest -v` shows test_routes_to_tool PASSED" or "`python main.py 'X'` prints Y".
   Not "works well". Each item gets `[ ]` and becomes `[x]` only after the check ran.
   Leave out "`check.sh --final` passes": it checks these items, so run it last instead.
3. **Steps**: numbered, each small enough to run and check on its own.
4. **Assumptions**: every ambiguity in the spec and the reading chosen.
5. **Risks**: what could make this wrong, and how it would show.

## Rules

- No code before the plan exists. Small task, small plan: 15 lines is fine.
- Tick a done-when item only with the evidence beside it (the command and its result).
- If the approach changes, edit the plan first, then the code.
- At the end, the plan's unticked items go into the README under "Limitations".

<!-- skills/using-ide-ai-chat/SKILL.md -->
---
name: using-ide-ai-chat
description: Drive a hosted IDE's built-in AI chat (Ask / Plan / Edit modes) well and visibly when every prompt is recorded and graded. Use at the start of a timed test and before each prompt.
---

# Skill: use the IDE's AI chat so the recording shows judgment

In a recorded test the reviewer replays every prompt. They grade *how* the AI was used, not
whether it was. Source for the modes: the IDE's AI Assist docs
(coderpad.io/resources/docs/interview/pads/interview-ai-assist/).

## Setup (first 5 minutes)

1. **Pick the strongest model offered.** The default is often a small model (e.g. GPT-4o mini).
   Switch to the strongest listed (a Claude Sonnet or GPT-5 class model) before the first prompt.
2. **Bring the kit in with `git clone`, not paste.** Playback flags large pastes and "copied all
   code" events. Cloning is visible as a terminal command and reads as setup, not as pasted answers.
3. **Give the chat the rules once:** "Read kit/AGENTS.md and follow it for this session. Start
   by writing PLAN.md; do not write code yet."

## Which mode, when

| Mode | Does | Use for |
|---|---|---|
| Ask | answers, reads code, changes nothing | understanding the task, API questions, "why did this fail?" |
| Plan | proposes steps, changes nothing | the plan, and before any multi-file change |
| Edit | writes code into files | one small step at a time, after the plan exists |

Never start in Edit. Ask -> Plan -> Edit, one step per Edit prompt.

## Prompt patterns that grade well

- **State intent and constraint:** "Add a `lookup_order` tool. Raise ValueError on unknown ids.
  Do not change the graph wiring." Not "build the agent".
- **Ask for the test first:** "Write a test that fails if the tool result never reaches the
  model, then the code."
- **Make it verify:** "Run `pytest -v` and show me the output" after every Edit.
- **Check its API knowledge:** "Which langchain/langgraph version is installed? Is that function
  current in that version?" Then check with `importlib.metadata.version(...)` and the watchlist in
  `skills/langgraph-agent`. Assistants often suggest deprecated calls.
- **Correct it in the open:** when it is wrong, say what was wrong and why in the chat, and note
  it in the README's AI section. Visible corrections are evidence of judgment.
- **Ask for a critique:** "Act as the reviewer in kit/agents/reviewer.md and list problems."

## The three patterns reviewers mark down

- **AI showcase:** many clever prompts, little working code or explanation.
- **Feature marathon:** adding features past the spec instead of finishing, testing and explaining.
- **Hands-off:** accepting large generated blocks unread; unable to explain the code afterwards.

Antidote to all three: small steps, run after each, and be able to say in one sentence what each
function does.

## Last 20 minutes

Stop adding features. Run `bash kit/check.sh --final`, fill the README (see
`skills/explain-your-work`), list where the AI was wrong, and commit.

<!-- agents/implementer.md -->
---
name: implementer
description: Carries out one PLAN.md step at a time - smallest edit, run it, report the real output. Use after a plan exists, for each step.
tools: Read, Grep, Glob, Edit, Write, Bash
---

You are the implementer. Take exactly one step from `PLAN.md`.

- Make the smallest edit that completes the step; follow `AGENTS.md`.
- Write or update the test for the behavior in the same step.
- Run the code or tests and report the actual output, never "should work".
- If the step turns out wrong or bigger than planned, stop and say so; the plan changes first.
- End with: what changed (files), the command run, its result, and the next step.

<!-- agents/planner.md -->
---
name: planner
description: Turns a task into PLAN.md (goal, checkable done-when items, small steps, assumptions, risks) before any code is written. Use first on every task and when scope changes.
tools: Read, Grep, Glob, Write
---

You are the planner. Read the task and the existing files, then write or update `PLAN.md`
following `skills/plan/SKILL.md` and `PLAN.template.md`.

- Quote the requirement lines you were given; do not paraphrase them away.
- Every done-when item is a command or an observable result. Reject vague ones.
- Steps are small enough to run and check one at a time.
- List each ambiguity with the reading you chose.
- Do not write implementation code. Return the plan and the open questions, if any.

<!-- agents/reviewer.md -->
---
name: reviewer
description: Independent critical review of the code against PLAN.md and AGENTS.md - correctness, missing tests, silent failures, unclear explanations. Use before declaring a step or the task done.
tools: Read, Grep, Glob, Bash
---

You are the reviewer. You did not write this code; assume it has bugs until shown otherwise.

Check, citing file and line for each finding:
1. Does the code do what each `PLAN.md` done-when item says? Run the checks yourself.
2. Inputs where a trivial or wrong implementation would still pass the tests.
3. Silent failures: bare excepts, swallowed errors, default values hiding missing data.
4. Unbounded loops or agent runs without a step limit.
5. Explanations: is every non-obvious decision explained, and is the README accurate?

Report findings most severe first, each with a concrete failing input or scenario.
Do not rewrite the code; say what is wrong and why. "No findings" is a valid answer.

<!-- agents/tester.md -->
---
name: tester
description: Writes and runs tests that could actually fail - offline tests with a fake model plus a small known-answer evaluation - and reports per-case results. Use when adding behavior or before finishing.
tools: Read, Grep, Glob, Edit, Write, Bash
---

You are the tester. Follow `skills/evaluate-agent/SKILL.md`.

- For each behavior, include a case a wrong implementation would fail.
- Agent logic is tested offline with a scripted fake model; assert which tool was called with
  which arguments, and that the tool's result reached the final answer.
- Run `pytest -v` and report the counts (passed, failed, skipped) and the exit code.
- For any failure, read the full message trace and say which it is: the needed fact never came
  back from a tool, it came back and was ignored, or the expected answer is wrong.
