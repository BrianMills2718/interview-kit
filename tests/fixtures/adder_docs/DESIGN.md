# Design

## Outcome
A caller adds two numbers and gets their sum back.

Example: add(2, 3) -> 5

## Requirements
| ID | Quoted from the task | Assumption, if inferred |
|---|---|---|
| R1 | "Add two numbers." | integers only |

## Failure modes and controls
| ID | Requirement | What could go wrong | Control (least code that prevents, detects or recovers) |
|---|---|---|---|
| F1 | R1 | subtracts instead of adding | test_add checks 2 + 3 = 5 |

## Domain rules, in the order they are checked
1. Both inputs are numbers: otherwise Python raises TypeError.

## Fixtures: one good and one smallest bad input per boundary
| Boundary | Good input | Bad input | Expected on bad |
|---|---|---|---|
| add | (2, 3) | ("a", 3) | TypeError |

## Slices: build order, each with its judge first
1. add: judged by `test_add`
