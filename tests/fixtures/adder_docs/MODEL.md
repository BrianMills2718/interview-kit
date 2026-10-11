# System model

## Goals
- Outcome: a caller adds two numbers and sees the sum.
- Quality goals: correct sum.

## 1. Context: who and what is outside the system?
```mermaid
flowchart LR
  Caller -->|two numbers| Adder
```

## 2. Building blocks: which part owns what?
```mermaid
flowchart TB
  add["add()"]
```

| Block | Owns | Code |
|---|---|---|
| adder | the sum | `add()` |

## 3. Main sequence: what happens, in order, on the main path?
```mermaid
sequenceDiagram
  participant Caller
  participant Adder
  Caller->>Adder: add(2, 3)
  Adder-->>Caller: 5
```

## 4. Rules: in what order are the business rules checked?
```mermaid
flowchart TD
  num{both numbers?} -->|yes| sum[return a + b]
  num -->|no| err[TypeError]
```

## 5. States: what states does the main item move through?
No states: add is a pure function.

## 6. Data: what are the typed contracts and state?
```mermaid
classDiagram
  class add {
    a: int
    b: int
  }
```

## Runtime: which function writes each record?
| Process | Trigger | Reads | Writes | Writer |
|---|---|---|---|---|
| add | a call | a, b | nothing | `add()` |

## Contracts: what crosses between parts, and how it fails
| Crossing | Producer | Consumer | Shape | On failure |
|---|---|---|---|---|
| call | Caller | add | two ints | TypeError |

## Quality: what observable result shows each goal holds?
| Goal | Observable pattern | Test |
|---|---|---|
| correct sum | 2 + 3 = 5 | `test_add` |

## Unknowns
| Unknown | What would decide it |
|---|---|
| floats allowed? | a task line saying so |
