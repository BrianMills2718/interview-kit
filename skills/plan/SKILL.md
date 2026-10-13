---
name: plan
description: Write a short PLAN.md before any code - the goal, checkable done-when items, numbered steps and risks - and keep it current. Use at the start of every task and whenever scope changes.
---

# Skill: plan before code

A plan is one short file, `PLAN.md`, written before the first code edit and updated as work
goes. It is the contract the checks in `check.sh` hold the work to. Copy `PLAN.template.md`.

## What goes in it

1. **Goal**: the task in your own words, 2-3 sentences. Quote the exact requirement lines
   from the prompt you were given.
2. **Done when**: checkable items, each one a command or an observable result, e.g.
   "`pytest -v` shows test_routes_to_tool PASSED" or "`python main.py 'X'` prints Y".
   Not "works well". Each item gets `[ ]` and becomes `[x]` only after the check ran.
   Leave out "`check.sh --final` passes": it checks these items, so run it last instead.
3. **Steps**: numbered, each small enough to run and check on its own.
4. **System model** (heading `## System model`): one line pointing at `docs/MODEL.md`. The
   planning package lives in `docs/`, copied from `templates/` and filled before code:
   - `docs/PRD.md`: goal with one example, quoted requirements R1.., use cases UC1.. (normal,
     failure, alternative), assumptions A1.., risks K1.. riskiest first (`method/design-chain.md`);
   - `docs/MODEL.md`: domain model (classDiagram and its rules), state machine
     (stateDiagram-v2 with the human pause and a Forbidden list, or "No states: <reason>"), the
     riskiest use case as a sequence diagram, and "Tests from the model": one test per state
     arrow and per forbidden line; other diagrams only when they answer a question
     (`method/system-model.md`, `method/architecture-views.md`);
   - `docs/DECISIONS.md`: one ADR row per real choice (`method/decisions.md`).
   `check.sh` fails until each is filled; `--final` also fails any function or test the model
   names that the code does not define.
5. **Assumptions**: every ambiguity in the spec and the reading chosen.
6. **Risks**: what could make this wrong, and how it would show.

## Choose the simplest shape that works (write the choice in the plan)

Adapted from github/awesome-copilot `agent-architecture` (MIT); see also Anthropic, "Building
effective agents". Graders reward saying why you did *not* build something bigger.

| If the task... | Build |
|---|---|
| has fixed rules and clear inputs | plain code; an LLM only for the fuzzy part |
| has all data available up front | one model call with validated structured output |
| has a known order of steps | a fixed workflow (chain or graph) with LLM steps inside |
| needs new observations to decide the next step | a bounded agent loop with tools |
| has independent subtasks needing separate context | a supervisor with specialists as tools |

Write one line per rejected shape: "Not an agent: every input is known before the call."

## Rules

- No code before the plan exists. Small task, small plan: 15 lines is fine.
- Write every done-when item as `[ ]`. Tick it only after its command ran, and replace the
  expected result with what it printed ("8 passed, 0 failed", not "N passed").
  `check.sh --final` fails a ticked item still showing "N passed".
- If the approach changes, edit the plan first, then the code.
- At the end, the plan's unticked items go into the README under "Limitations".
