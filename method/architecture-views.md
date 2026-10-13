# Architecture views: which diagram for which question

Draw a view only to answer a question someone has. In a take-home, `docs/MODEL.md` always has
the domain model, the state machine and the riskiest use case as a sequence; add another view
from this table only when it answers a question. Pick the view from the concern:

| Concern | View | In Mermaid |
|---|---|---|
| scope: who uses it, what is outside | C4 context | `flowchart LR` with people and external systems |
| ownership: which part does what | component view plus a responsibility table | `flowchart` with one box per part |
| domain terms | glossary, with a class or ER diagram if terms relate | `classDiagram`, `erDiagram` |
| crossings between parts | contract table: producer, consumer, shape, failure | a table, not a diagram |
| order of steps and failures | sequence or activity diagram | `sequenceDiagram`, `flowchart TD` |
| states an item moves through | state machine | `stateDiagram-v2` |
| where it runs | deployment, only when placement matters | `flowchart` |
| claims: why we believe it works | traceability table | a table |

Rules:

- **Bind every view to the source.** Each box or arrow names a real file, function, tool or
  record. A box you cannot point at is a guess; mark it.
- **Label each view** `current` (what the code does), `proposed` (the plan) or `historical`.
- **An ownership arrow is not a data-flow arrow.** Use one kind of arrow per diagram and say in
  the caption which.
- **A straight chain is a numbered list**, not a diagram.
- **Reconcile** the views with each other before coding, and again after any change that
  touches a part they show.

## Traceability: the chain a reviewer follows

requirement → domain rule → operation → contract → check (one passing case, one rejected case)
→ observation (the test output that shows it).

As a table in the README:

| Requirement (quoted) | Rule | Code | Check | Seen |
|---|---|---|---|---|
| "refunds over $50 need approval" | amount > 50 pauses | `request_refund` | `test_large_refund_pauses`, `test_small_refund_does_not` | pytest output |

Adapted from ISO/IEC/IEEE 42010 (views answer stakeholders' concerns), UML and the C4 model.
