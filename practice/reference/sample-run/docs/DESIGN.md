# Design

Filled from `kit/templates/DESIGN.md` before the code. The task fixes inputs, outputs and rules,
so most lines quote it.

## Outcome
A shop customer sends one message and gets a validated `Reply` (category, order id, one-sentence
action, policy ids), with any allowed refund recorded and any refund over $50 approved by a human first.

Example: "Please refund my desk lamp, order A-101" -> tools return `A-101: Desk lamp, $30, delivered 2026-02-20`
and `Refunded A-101 ($30).`; `shop["refunds"] == ["A-101"]`; `Reply(category="refund", order_id="A-101", action="Refunded order A-101.", policy_ids=["P-1"])`.

## Requirements
| ID | Quoted from the task | Assumption, if inferred |
|---|---|---|
| R1 | "`get_order(order_id)` ... `A-101: Desk lamp, $30, delivered 2026-02-20` (date only once delivered), or `Order A-999 not found.`" | not-delivered orders show their status word: `A-103: Monitor, $80, processing` |
| R2 | "`search_policy(query)` ... best matching policies, best first, at most 2 ... `P-2: <policy text>`, or `No matching policy.`" | keyword overlap; ties keep data order |
| R3 | "Unknown order: `Order X not found.`" | none |
| R4 | "Already refunded: `X was already refunded.`" | none |
| R5 | "Not delivered: `Not eligible: X has not been delivered.`" | none |
| R6 | "Delivered more than 30 days before today: `Not eligible: X was delivered N days ago (limit 30).`" | today is `data.json` "today"; 30 days exactly is allowed |
| R7 | "Amount over $50: pause and ask a human reviewer, before refunding. On `yes`: `Refunded X ($N) after approval.` Otherwise: `Refund for X declined by reviewer.`" | only `yes` approves |
| R8 | "Otherwise: `Refunded X ($N).`" | none |
| R9 | "A refund is recorded by appending the order id to `shop[\"refunds\"]`." | only after every check and any approval |
| R10 | "The final answer is a validated `Reply` ... An invalid answer goes back to the model to retry." | none |
| R11 | "`build_agent(llm, shop)` ... return a compiled graph with a checkpointer" | none |

## Failure modes and controls
| ID | Requirement | What could go wrong | Control (least code that prevents, detects or recovers) |
|---|---|---|---|
| F1 | R7, R9 | tool re-runs from the top on resume and refunds twice | write only after `interrupt()` returns; rules re-checked on resume (rule 2 then blocks a repeat) |
| F2 | R3-R8 | rules checked in the wrong order (e.g. old and over $50 asks a reviewer) | one pure function `refund_refusal()` checks rules 1-4 in order before any pause |
| F3 | R10 | model returns an invalid Reply (bad category, bad order id) | Pydantic `Reply` via `ToolStrategy`: the validation error goes back to the model |
| F4 | R2 | wrong policy ranked first, or more than 2 returned | `score_policy()` plus a `[:2]` cut; test with a query where a naive "first policy" answer is wrong |
| F5 | R11 | a looping model never stops | `recursion_limit` set on the compiled graph at build time |
| F6 | R1 | order id typed in lower case or with spaces | `normalize_order_id()` upper-cases and strips |

## Domain rules, in the order they are checked
1. Unknown order: return `Order X not found.`
2. Already in `shop["refunds"]`: return `X was already refunded.`
3. Status is not delivered: return `Not eligible: X has not been delivered.`
4. Delivered more than 30 days before today: return `Not eligible: X was delivered N days ago (limit 30).`
5. Amount over $50: pause for a reviewer; `yes` -> record and `Refunded X ($N) after approval.`; else `Refund for X declined by reviewer.`
6. Otherwise: record and return `Refunded X ($N).`

## Fixtures: one good and one smallest bad input per boundary
| Boundary | Good input | Bad input | Expected on bad |
|---|---|---|---|
| model -> `get_order` | `A-101` | `A-999` | `Order A-999 not found.` |
| model -> `search_policy` | `refund my lamp` | `hello` | `No matching policy.` |
| model -> `request_refund` | `A-101` | `A-104` (50 days old) | `Not eligible: A-104 was delivered 50 days ago (limit 30).` |
| reviewer -> resume | `yes` | `no` | `Refund for A-102 declined by reviewer.`, nothing recorded |
| model -> `Reply` | `category="refund", order_id="A-101"` | `category="billing"` | validation error sent back; model retries |

## Slices: build order, each with its judge first
1. Order lookup and policy search tools: judged by `test_get_order_formats` and `test_search_policy_ranks_best_first`.
2. Refund rules 1-4 and small refund: judged by `test_refund_rules_in_order` and `test_small_refund_recorded_once`.
3. Approval pause over $50: judged by `test_large_refund_approved_after_pause` and `test_large_refund_declined_records_nothing`.
4. Validated final answer with retry: judged by `test_invalid_reply_is_retried`.
5. Whole system: judged by `kit/practice/grade.py`.
