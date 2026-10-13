# PRD: order-support agent

Written top to bottom before the code; the task fixes inputs, outputs and rules, so they are quoted.

## Goal
A customer sends one message; the agent looks up facts with tools, refunds only when the rules
allow (asking a human reviewer first for refunds over $50), and returns a validated `Reply`. One
agent with three tools, because the rules are a fixed chain inside one tool and only the order of
lookups varies.

Example: "Please refund A-101, the lamp is not what I wanted." -> `request_refund` returns
`Refunded A-101 ($30).`, `shop["refunds"] == ["A-101"]`, Reply(category="refund", order_id="A-101", ...).

## Requirements
| ID | Quoted from the task | Reading chosen, if ambiguous |
|---|---|---|
| R1 | "`get_order(order_id)` ... `A-101: Desk lamp, $30, delivered 2026-02-20` (date only once delivered), or `Order A-999 not found.`" | not delivered shows the status: `A-103: Monitor, $80, processing` |
| R2 | "`search_policy(query)` find the best matching policies, best first, at most 2 ... or `No matching policy.`" | best = most shared words; zero shared words = no match |
| R3 | "Refund rules, checked in this order" (1 to 6) | "more than 30 days" means `days > 30` |
| R4 | "Amount over $50: pause and ask a human reviewer, before refunding." | over = strictly greater than 50; only "yes" approves |
| R5 | "A refund is recorded by appending the order id to `shop["refunds"]`." | none |
| R6 | "The final answer is a validated `Reply` ... An invalid answer goes back to the model to retry." | `order_id` = `A-` plus digits |
| R7 | "return a compiled graph with a checkpointer" | none |

## Use cases
| ID | Kind | Actor | Trigger | Steps | Expected result |
|---|---|---|---|---|---|
| UC1 | normal | customer | "refund A-101" ($30, 9 days) | look up order, check rules, refund | `Refunded A-101 ($30).`, refunds = [A-101], a `Reply` |
| UC2 | alternative | customer, reviewer | "refund A-102" ($120) | rules pass, pause, reviewer says yes, resume | `Refunded A-102 ($120) after approval.`, A-102 recorded once |
| UC3 | failure | customer, reviewer | "refund A-102", reviewer says no | rules pass, pause, resume with "no" | `Refund for A-102 declined by reviewer.`, nothing recorded |
| UC4 | failure | customer | "refund A-104" (50 days) | rule 4 matches | `Not eligible: A-104 was delivered 50 days ago (limit 30).` |
| UC5 | failure | customer | "refund A-999" | rule 1 matches | `Order A-999 not found.` |
| UC6 | failure | model | `Reply` with category `billing` | validation fails, error sent back | the model retries; no invalid `Reply` returned |
| UC7 | normal | customer | "what is the refund window?" | search policies | best policy first, at most 2 |

## Assumptions
| ID | Assumption | Requirement it affects |
|---|---|---|
| A1 | exactly 30 days is still refundable | R3 |
| A2 | exactly $50 is refunded without review | R4 |
| A3 | only the word "yes" approves; anything else declines | R4 |
| A4 | a live model picks the right tools from these docstrings (guessed) | R6 |

## Risks
| ID | Risk | Use case | How we test it early |
|---|---|---|---|
| K1 | the refund is written before the reviewer answers, or twice when the tool re-runs on resume | UC2, UC3 | `probe_interrupt.py` first, then `test_large_refund_pauses_then_approves` and `test_large_refund_declined_records_nothing` |
| K2 | rules checked out of order | UC4, UC5 | `test_refund_rules_in_order` |
| K3 | a bad `Reply` is accepted | UC6 | `test_reply_rejects_bad_values`, `test_invalid_reply_goes_back_for_retry` |
| K4 | a looping model never stops | UC1 | `test_looping_model_is_stopped` |
