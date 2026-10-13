---
name: explain-your-work
description: Write the README and in-code explanations reviewers read first, including how the AI assistant was used. Use at the end and keep updated while working.
---

# Skill: explain the solution

Use at the end, and keep it updated while working. Reviewers read this first.

## README template

```markdown
# <Task name>

## Run it
<one command>  ->  <what you should see>
Tests: `pytest -v`  ->  N passed

## Approach
Two or three sentences: what the system does and the shape of the solution (a diagram line
like START -> agent -> tools -> agent -> END helps).

## Design decisions
The two or three that matter most; all of them are in [docs/DECISIONS.md](docs/DECISIONS.md).
Requirements, use cases and risks: [docs/PRD.md](docs/PRD.md); the model: [docs/MODEL.md](docs/MODEL.md).
Paste the state machine and the riskiest use case's sequence diagram from the model here.

| Requirement | Code | Test |
|---|---|---|
| R1 "<quoted line>" | `<function()>` | `<test name>` |

## Assumptions
Where the spec was ambiguous and which reading I chose.

## How I used the AI assistant
- What I delegated (boilerplate, test cases, API lookups) and what I kept (design, review).
- Where its suggestion was wrong or I changed it, and how I caught it (a failing test, a run).

## Limitations and next steps
What breaks, what is untested, and what I would do with more time.
```

## In the code

- Module docstring at the top: what this file is for.
- One-line docstring per function; comments only for non-obvious "why".
