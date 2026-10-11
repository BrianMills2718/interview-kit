# Plan

## Goal
Build a support agent for a small shop that answers one customer message by calling three tools
(`get_order`, `search_policy`, `request_refund`) and ending with a validated `Reply`. Refunds over
$50 pause for a human reviewer and only happen on "yes".

Quoted: "Build a customer-support agent for a small shop, with LangGraph or LangChain, in `solution.py`."
"Refund rules, checked in this order: 1. Unknown order ... 6. Otherwise: `Refunded X ($N).`"
"A refund is recorded by appending the order id to `shop["refunds"]`."
"The final answer is a validated `Reply` ... An invalid answer goes back to the model to retry."
"def build_agent(llm, shop): ... return a compiled graph with a checkpointer"

## Done when
- [x] `.venv/bin/python kit/practice/grade.py solution.py` -> `== grade: 8 passed, 0 failed of 8 cases`, exit 0
- [x] `.venv/bin/python -m pytest -v test_solution.py` -> `9 passed`, none skipped
- [x] `.venv/bin/python probe_interrupt.py` -> caller got `__interrupt__` with the payload, checkpoint next node `('tools',)`, `risky() entered 2 times`
- [x] README explains approach, decisions, AI use and limitations (Run it, Approach, Design decisions, AI, Limitations sections present)

## Steps
1. Tests for `get_order` and the six refund rules (small refund, pause, approve, decline), then the tool code.
2. Test and code for `search_policy` (best first, at most 2, `No matching policy.`).
3. `Reply` model with validators; test that a bad reply is rejected.
4. `build_agent()` with `create_agent` + `ToolStrategy(Reply)` + `InMemorySaver`; end-to-end test with a scripted model.
5. Probe script that runs the pause/resume and logs each entry into `request_refund`; check the re-run claim.
6. Grade, fix, update MODEL.md to current, README.

## Shape
Bounded agent loop with tools (`create_agent`): the next tool depends on what the last one returned
(order found? delivered?). Not plain code: the customer message is free text and the model picks
the tools. Not one structured call: order and policy facts are not known before the call.
Not a supervisor: one small domain, no independent subtasks.

## System model
See docs/MODEL.md. Key facts: all refund rules live in plain Python inside `request_refund()`, and
the approval pause is `interrupt()` inside that tool, so on resume the tool re-runs from its first
line; the refund is appended only after `interrupt()` returns "yes".

## Assumptions
- "more than 30 days" -> `(today - delivered_on).days > 30` is ineligible; exactly 30 is allowed.
- "Amount over $50" -> strictly greater than 50; $50 exactly refunds without review.
- Reviewer answer -> only the string "yes" (case-insensitive, trimmed) approves; anything else declines.
- `search_policy` "best matching" -> count of shared lowercase words (ignoring short stop words); ties keep policy order; zero shared words is no match.
- `order_id` "A-123 form" -> `A-` followed by digits.
- "one sentence" -> non-empty and no sentence end followed by more text.

## Risks (failure modes)
- Refund appended before the reviewer answers (e.g. code before `interrupt()`) -> a declined case shows the id in `shop["refunds"]`.
- Tool re-run on resume double-refunds -> refunds list has the id twice.
- Policy scoring ranks wrongly -> grader `tool_output_contains` fails on a policy case.
- Model loops -> recursion limit error instead of an answer.
