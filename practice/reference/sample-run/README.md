# Order-support agent

## Run it
```bash
uv venv && uv pip install langchain langgraph pytest
.venv/bin/python kit/practice/grade.py solution.py   # -> == grade: 8 passed, 0 failed of 8 cases
```
Tests: `.venv/bin/python -m pytest -v test_solution.py` -> 11 passed.

## Approach
`build_agent(llm, shop)` returns LangChain's `create_agent` graph:
`START -> model -> tools -> model ... -> Reply -> END`, compiled with an `InMemorySaver`
checkpointer. The three tools are closures over `shop`. `request_refund` checks the rules in the
task's order; over $50 it calls `interrupt()` and records the refund only after the reviewer's
answer comes back. The final answer is `ToolStrategy(Reply)`: the model calls a `Reply` tool,
Pydantic validates it, and a validation error goes back to the model to retry.

## Design decisions
| Decision | Why | Rejected alternative | What would show it wrong |
|---|---|---|---|
| `create_agent` + `ToolStrategy(Reply)` | gives tool loop, retry on invalid Reply and `structured_response` for free | hand-built `StateGraph` with a final `with_structured_output` node (more code, the grader's model replies via a `Reply` tool call anyway) | a need for custom routing between tools |
| `interrupt()` inside the refund tool, write after it | the tool re-runs from the top on resume, so writing before the pause would double-refund | separate approval node (needs extra state to carry order id/amount) | refunds list showing a duplicate id (tested) |
| tools as closures over `shop` | each graph sees its own data; the grader passes a fresh `shop` per case | module-level globals | tests leaking refunds between cases |
| keyword-overlap policy search | offline, deterministic, 3 policies | embeddings | a query whose words do not appear in the right policy |

## Assumptions
- "More than 30 days" means refused when days > 30; exactly 30 is allowed.
- "Over $50" means amount > 50.
- Any reviewer answer other than "yes" (case-insensitive, trimmed) is a decline.
- `get_order` prints the date only for status `delivered`, else just the status.

## How I used the AI assistant
The whole session was run by an AI coding agent (Claude) following `kit/AGENTS.md`, as a
rehearsal; no separate chat. It wrote the plan, tests and code. Where it changed course:
it first pre-ticked the plan's done-when items before running anything and then unticked them
(the kit rule is to tick only with evidence); it removed an unneeded `__main__` block it had
started. The kit's API watchlist (interrupt re-runs the tool) shaped the refund code before any
failure happened. All 8 grader cases passed on the first grade run; `cases.json` was read only after it.

## Limitations and next steps
- No live-model entry point: the agent is only run with scripted models (grader and tests).
  Next: a `main()` that builds a provider model from an env key and fails clearly without it.
- No step limit is set inside the graph; callers must pass `recursion_limit` (the grader passes 50).
- Step logging is minimal (only the reviewer's answer is logged); no per-node trace.
- Policy search is keyword overlap; synonyms ("money back") will not match.
