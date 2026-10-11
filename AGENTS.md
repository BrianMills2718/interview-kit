# Working rules for the coding assistant

These rules apply to any AI coding assistant working in this project. Read them before acting.

## How we work

1. **Plan before code.** Write `PLAN.md` from `PLAN.template.md` (see `skills/plan/SKILL.md`):
   goal with the quoted requirements, checkable done-when items, small steps, the shape chosen,
   assumptions and risks. With it, fill the planning package from `kit/templates/`:
   `docs/DESIGN.md` (outcome, quoted requirements, failure modes, rules, fixtures, slices),
   `docs/MODEL.md` (six Mermaid diagrams: context, building blocks, main sequence, rules,
   states, data; plus runtime, contracts, quality and unknowns tables) and `docs/DECISIONS.md`.
   `check.sh` fails until all three are filled in. How to think at each stage is in
   `kit/method/README.md`.
   Wait for approval before editing code (the person types "plan approved" in the chat, so the
   recording shows it). If no person is present (an agent working alone or rehearsing), commit
   the plan and go on: the commit is the record.
2. **One small step at a time.** Each edit does one thing that can be run and checked. No
   multi-file rewrites in one go.
3. **Run it after every change.** Execute the code or the tests after each edit and report the
   actual output. Never say "this should work" without running it.
4. **Tests define done.** Write a small test for each behavior before or with the code. Include
   at least one case where a trivial or wrong implementation would fail.
5. **Fail loudly.** No bare `except:`, no silent fallbacks that hide errors. Raise or log with
   context. A missing API key or bad input is an error message, not an empty result.
6. **Keep it simple.** Standard library and the libraries already in use first. No new
   dependency or abstraction without a stated reason.
7. **Explain as you go.** Every function has a one-line docstring saying what it does and why.
   Non-obvious decisions get a short comment naming the alternative that was rejected.
8. **Say when unsure.** If the spec is ambiguous, state the interpretation chosen and why,
   in the code and in the README, rather than guessing silently.

## Roles (subagents)

Work in four roles, one at a time, each described in `agents/`: **planner** writes `PLAN.md`,
**implementer** does one step and runs it, **tester** writes tests that could fail, **reviewer**
critiques the result against the plan before anything is called done. When asked to act as a
role, follow that file.

## Enforcement

`bash kit/check.sh` checks the plan is concrete, the code compiles and the tests pass, and prints
counts. `bash kit/check.sh --final` also requires every done-when item ticked and the README
sections present. Run it after each step; the work is done only when `--final` passes.

## Agentic AI specifics

- Typed state and typed outputs: `TypedDict` for graph state, Pydantic models for structured
  LLM output (`llm.with_structured_output(Model)`), validated, never parsed with regex.
- Tools have precise names, docstrings and typed arguments: the docstring *is* the prompt the
  model sees. Tools return short, structured strings or dicts and raise clear errors.
- Bound every loop: a maximum number of steps (`recursion_limit`) and an explicit stop condition.
- Keep the LLM swappable: one function builds the model; tests use a fake model so they run
  offline and deterministically.
- Log each step (node name, tool called, arguments, result size) so a run can be traced.
- Evaluate with a handful of concrete cases with known answers, including a failure case;
  report pass/fail per case, not a single score.

## Final deliverable checklist

- [ ] Runs end to end from one command shown in the README.
- [ ] Tests pass; the README shows the command and the result.
- [ ] README: approach, design decisions and rejected alternatives, assumptions, limitations,
      what I would do next with more time.
- [ ] Places where the AI's suggestion was wrong or changed, and why, are noted.
