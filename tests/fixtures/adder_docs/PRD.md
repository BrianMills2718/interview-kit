# PRD: adder

## Goal
A caller adds two numbers and gets their sum back, with one pure function.

Example: add(2, 3) -> 5

## Requirements
| ID | Quoted from the task | Reading chosen, if ambiguous |
|---|---|---|
| R1 | "Add two numbers." | integers only |

## Use cases
| ID | Kind | Actor | Trigger | Steps | Expected result |
|---|---|---|---|---|---|
| UC1 | normal | caller | two ints | call add | their sum |
| UC2 | failure | caller | a string | call add | TypeError |

## Assumptions
| ID | Assumption | Requirement it affects |
|---|---|---|
| A1 | floats are out of scope | R1 |

## Risks
| ID | Risk | Use case | How we test it early |
|---|---|---|---|
| K1 | subtracts instead of adding | UC1 | test_add checks 2 + 3 = 5 |
