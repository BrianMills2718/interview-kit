# PRD: <system name>

Copy to `docs/PRD.md` in the first minutes, before the model and the code. Fill it top to
bottom (method/design-chain.md): goal, quoted requirements, use cases (the normal path first, then
what goes wrong), assumptions, risks ranked riskiest first. The row ids (`R1`, `UC1`, `A1`, `K1`)
are the kit's own convention so the model, plan and tests can point at rows.
Guidance in `<!-- -->` comments does not render; leave or delete it.

## Goal
<one-line thesis: who uses it, what they get, why this shape>

Example: <one concrete input> -> <the exact expected result>

## Requirements
| ID | Quoted from the task | Reading chosen, if ambiguous |
|---|---|---|
| R1 | "<exact requirement text>" | <reading, or none> |

## Use cases
<!-- Kind is normal, failure or alternative. At least one normal and one failure or alternative.
Steps are short: actor action, system response. -->
| ID | Kind | Actor | Trigger | Steps | Expected result |
|---|---|---|---|---|---|
| UC1 | normal | <actor> | <what starts it> | <steps> | <what they see> |
| UC2 | failure | <actor> | <what goes wrong> | <steps> | <error or refusal they see> |

## Assumptions
| ID | Assumption | Requirement it affects |
|---|---|---|
| A1 | <answer to an open question> | <R1> |

## Risks
<!-- Riskiest first. The riskiest use case gets the sequence diagram in docs/MODEL.md and is
built first. -->
| ID | Risk | Use case | How we test it early |
|---|---|---|---|
| K1 | <what could go wrong> | <UC2> | <the test or probe that would show it> |
