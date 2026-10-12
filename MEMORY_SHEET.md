# Memory sheet: the method with no kit files

For a test that allows no outside files. Learn this page; every line can be typed from memory.

## First message to the IDE's assistant (type it, it is recorded)
> Work with me in small steps. Plan before code: we write PLAN.md and docs/ first, and I approve
> before any code. After every change, run the tests and show the real output. Write a test
> that a wrong version would fail. No bare except, no silent fallbacks. One-line docstring on
> every function. If the task is unclear, say which reading you chose and why.

## Files, in the order you write them
1. `PLAN.md`: goal (quote the task), done-when list you can check, 5 to 8 small steps, assumptions, risks.
2. `docs/DESIGN.md`: Outcome · Requirements (R1, R2… quoted) · Failure modes · Rules in check
   order · Fixtures (one good, one smallest bad per boundary) · Slices (build order).
3. `docs/MODEL.md`: six Mermaid diagrams. Each has a heading that asks a question and a
   bold **Answer:** line under it.
   1. Context (flowchart): who and what is outside?
   2. Agent loop (flowchart): which part runs each step, and where does it stop or pause?
   3. Main sequence (sequenceDiagram): caller, graph, model, tool, in order.
   4. Rules (a table in check order, plus a flowchart only for the branches).
   5. States (stateDiagram): running, paused, resumed, done.
   6. Data (classDiagram): State, tool inputs, the final answer model.
   Then four tables: Runtime (which function writes what), Contracts, Quality (goal, test), Unknowns.
4. `docs/DECISIONS.md`: rows D1, D2…: choice · why · rejected alternative · what would prove it wrong.
5. `solution.py`, `test_solution.py`: one slice at a time; tests first or alongside.
6. `README.md`: Run it · Approach (paste diagrams 2 and 4) · Design decisions · Assumptions ·
   How I used the AI assistant (where it was wrong and what I changed) · Limitations and next steps.

## Four hours
| Time | Do |
|---|---|
| 0:00-0:30 | read the task twice; PLAN.md; quote the requirements |
| 0:30-1:00 | DESIGN, MODEL, DECISIONS (rough is fine, fix later) |
| 1:00-2:45 | build slice by slice; run tests after each change |
| 2:45-3:30 | failure cases; make the diagrams match the code; README |
| 3:30-4:00 | buffer; run everything once more from a clean start; submit |

## LangChain / LangGraph calls the assistant gets wrong
- `create_react_agent` → `from langchain.agents import create_agent`
- `prompt=` / `state_modifier=` → `system_prompt=`
- Structured answer: `response_format=ToolStrategy(Model)`, read `out["structured_response"]`
- Bound the loop: `.with_config({"recursion_limit": 10})` (the default is far higher)
- Human pause: `interrupt()` returns `__interrupt__` to the caller; resume with
  `Command(resume=...)` on the same `thread_id`. **The tool re-runs from its first line**,
  so do the refund or write only after `interrupt()` returns.
- Tests use a fake, scripted model so they run offline.

## Mermaid breakers
No `;` inside a sequence message. No parentheses in a class field. Quote labels with
parentheses: `A["get_order()"]`. Paste each block into mermaid.live once to see it render.
