# Plan

## Goal
A customer writes to a small shop; a LangGraph agent looks up the order, finds the matching
policy, refunds when the rules allow (pausing for a human reviewer over $50), and returns a
validated `Reply`. Quoted requirements:
- "The agent answers a customer message using three tools, then gives a final structured answer."
- "`get_order(order_id)` ... Returns exactly `A-101: Desk lamp, $30, delivered 2026-02-20` (date only once delivered), or `Order A-999 not found.`"
- "`search_policy(query)` find the best matching policies, best first, at most 2 ... lines `P-2: <policy text>`, or `No matching policy.`"
- "Refund rules, checked in this order" (unknown, already refunded, not delivered, over 30 days, over $50 needs approval, otherwise refund).
- "A refund is recorded by appending the order id to `shop[\"refunds\"]`."
- "The final answer is a validated `Reply` ... An invalid answer goes back to the model to retry."
- "`def build_agent(llm, shop)` ... return a compiled graph with a checkpointer"

## Done when
- [x] `.venv/bin/python kit/practice/grade.py solution.py` -> `== grade: 8 passed, 0 failed of 8 cases`, exit 0
- [x] `.venv/bin/python -m pytest -v test_solution.py` -> `8 passed in 0.94s`, none skipped
- [x] `npx --yes @mermaid-js/mermaid-cli@11.4.2 -p .render/puppeteer.json -i docs/MODEL.md -o .render/MODEL.md` -> 6 of 6 diagrams rendered, exit 0 (needed `-p`: see README)
- [x] README explains approach, decisions, AI use and limitations (sections Run it, Approach, Design decisions, How I used the AI assistant, Limitations)

## Steps
1. Planning package: PLAN.md, docs/DESIGN.md, docs/MODEL.md, docs/DECISIONS.md; render the diagrams; commit.
2. Pure helpers + `get_order` / `search_policy` tools: tests first (format, not found, ranking, limit 2, no match).
3. `refund_refusal()` rules 1-4 and `request_refund` tool with the $50 approval `interrupt()`: tests for each rule, approve, decline.
4. `Reply` model and `build_agent()` with `create_agent(..., response_format=ToolStrategy(Reply), checkpointer=InMemorySaver())`: retry test with an invalid Reply.
5. First grade run; read every failing case's trace; fix; keep each fixed case as a test.
6. README per skills/explain-your-work; `check.sh --final`.

## Shape
Bounded agent loop with tools (`create_agent`), plus one human-approval pause inside the refund tool.
Not plain code: the customer message is free text and which order/policy to look up is decided from it.
Not a fixed workflow: the next tool depends on what the previous one returned (not found, not eligible).
Not a supervisor: one small domain, no independent subtasks needing separate context.

## System model
See [docs/MODEL.md](docs/MODEL.md). Key facts: all refund rules live in one pure function,
`refund_refusal()`, checked before the approval pause; the only write is `record_refund()`,
which runs after `interrupt()` returns, so a resumed tool cannot refund twice.

## Assumptions
- "Delivered more than 30 days before today" -> refuse only when days > 30; exactly 30 is allowed (the word is "more than").
- "Amount over $50" -> amount > 50; exactly $50 refunds without review.
- Reviewer answer -> only `yes` (case-insensitive, trimmed) approves; anything else declines, as "Otherwise" says.
- `order_id` in `Reply` "or none" -> `None` (JSON null); a string like "none" is rejected so the model retries.
- "action (one sentence)" -> a non-empty string with at most one sentence end; more is sent back to the model.
- Policy matching -> keyword overlap with light stemming; ties keep the data order (P-1 before P-2).
- Money printed as whole dollars (`$30`), as in the example; data amounts are integers.

## Risks (failure modes)
- Refund issued twice when the tool re-runs on resume -> `shop["refunds"]` shows the id twice; test resumes and asserts exactly one.
- Policy search ranks the wrong policy first -> grader `reply.policy_ids` or tool output mismatch.
- Reply schema too strict (rejects a valid scripted answer) or too loose (accepts invalid) -> grader "no structured_response" or wrong retry behavior.
- Agent loops forever -> recursion limit set at build time stops it with an error.
