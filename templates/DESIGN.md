# Design

Copy to `docs/DESIGN.md` in the first minutes, before the model and the code. Walk it top to
bottom (method/design-chain.md); each section depends on the one above. Short lists are fine.

## Outcome
<who does what, and what they see when it works, in one sentence>

Example: <one concrete input> -> <the exact expected result>

## Requirements
| ID | Quoted from the task | Assumption, if inferred |
|---|---|---|
| R1 | "<exact requirement text>" | <reading chosen, or none> |

## Failure modes and controls
| ID | Requirement | What could go wrong | Control (least code that prevents, detects or recovers) |
|---|---|---|---|
| F1 | R1 | <failure> | <control> |

## Domain rules, in the order they are checked
1. <rule>: <what happens>

## Fixtures: one good and one smallest bad input per boundary
| Boundary | Good input | Bad input | Expected on bad |
|---|---|---|---|
| <boundary> | <good> | <bad> | <error or refusal> |

## Slices: build order, each with its judge first
1. <slice>: judged by `<test name>`
