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
4. **Assumptions**: every ambiguity in the spec and the reading chosen.
5. **Risks**: what could make this wrong, and how it would show.

## Rules

- No code before the plan exists. Small task, small plan: 15 lines is fine.
- Tick a done-when item only with the evidence beside it (the command and its result).
- If the approach changes, edit the plan first, then the code.
- At the end, the plan's unticked items go into the README under "Limitations".
