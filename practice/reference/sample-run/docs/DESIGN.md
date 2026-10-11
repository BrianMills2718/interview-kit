# Design

Walked top to bottom before the code; the task fixes inputs, outputs and rules, so they are quoted.

## Outcome
A customer sends one message; the agent looks up facts with tools, refunds only when the rules
allow (asking a human reviewer first for refunds over $50), and returns a validated `Reply`.

Example: "Please refund A-101, the lamp is not what I wanted." -> `request_refund` returns
`Refunded A-101 ($30).`, `shop["refunds"] == ["A-101"]`, Reply(category="refund", order_id="A-101", ...).

## Requirements
| ID | Quoted from the task | Assumption, if inferred |
|---|---|---|
| R1 | "`get_order(order_id)` ... `A-101: Desk lamp, $30, delivered 2026-02-20` (date only once delivered), or `Order A-999 not found.`" | not delivered shows the status: `A-103: Monitor, $80, processing` |
| R2 | "`search_policy(query)` find the best matching policies, best first, at most 2 ... or `No matching policy.`" | best = most shared words; zero shared words = no match |
| R3 | "Refund rules, checked in this order" (1 to 6) | "more than 30 days" means `days > 30` |
| R4 | "Amount over $50: pause and ask a human reviewer, before refunding." | over = strictly greater than 50; only "yes" approves |
| R5 | "A refund is recorded by appending the order id to `shop["refunds"]`." | none |
| R6 | "The final answer is a validated `Reply` ... An invalid answer goes back to the model to retry." | `order_id` = `A-` plus digits |
| R7 | "return a compiled graph with a checkpointer" | none |

## Failure modes and controls
| ID | Requirement | What could go wrong | Control (least code that prevents, detects or recovers) |
|---|---|---|---|
| F1 | R3 | rules checked out of order (e.g. 30-day check before already-refunded) | one function with the checks as an if-chain in the stated order; a test per rule |
| F2 | R4, R5 | refund written before the reviewer answers, or written twice when the tool re-runs on resume | append only after `interrupt()` returns; test for decline leaves `refunds` empty, approve gives exactly one entry |
| F3 | R6 | model returns a bad category or order id and it is accepted | Pydantic `Literal` and validators on `Reply`; `ToolStrategy` returns the error to the model |
| F4 | R2 | weak query matches everything or nothing | score > 0 required, top 2 only; tests for a hit and for no match |
| F5 | R7 | resume without checkpointer loses the paused run | compile with `InMemorySaver`; end-to-end pause/resume test |

## Domain rules, in the order they are checked
1. Unknown order: `Order X not found.`
2. Already refunded: `X was already refunded.`
3. Not delivered: `Not eligible: X has not been delivered.`
4. Delivered more than 30 days before today: `Not eligible: X was delivered N days ago (limit 30).`
5. Amount over $50: pause for the reviewer; "yes" -> `Refunded X ($N) after approval.`, else `Refund for X declined by reviewer.`
6. Otherwise: `Refunded X ($N).`

## Fixtures: one good and one smallest bad input per boundary
| Boundary | Good input | Bad input | Expected on bad |
|---|---|---|---|
| `get_order` | `A-101` | `A-999` | `Order A-999 not found.` |
| `search_policy` | `refund window` | `zebra` | `No matching policy.` |
| `request_refund` | `A-101` ($30, 9 days) | `A-104` (50 days) | `Not eligible: A-104 was delivered 50 days ago (limit 30).` |
| reviewer answer | `yes` | `no` | `Refund for A-102 declined by reviewer.`, no refund recorded |
| `Reply` | category `refund`, order `A-101` | category `billing` | ValidationError sent back to the model |

## Slices: build order, each with its judge first
1. order lookup: judged by `test_get_order_delivered_and_missing`
2. refund rules 1-4 and 6: judged by `test_refund_rules_in_order`
3. approval pause: judged by `test_large_refund_pauses_then_approves` and `test_large_refund_declined_records_nothing`
4. policy search: judged by `test_search_policy_best_first_and_no_match`
5. Reply validation: judged by `test_reply_rejects_bad_values`
6. wiring end to end: judged by `test_agent_end_to_end_small_refund` and the grader
