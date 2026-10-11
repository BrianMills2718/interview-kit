---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v2-practice
plan_id: kit-v2-practice
status: proposed
planning_path: requested
method_conformance_receipt: docs/plans/kit-v2-practice.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "practice/ holds a spec, data, known-answer cases and a grader; a hidden reference passes and a broken one fails"
  canonical_example: "python practice/grade.py with the reference solution prints 7/7 cases PASS"
  forbidden_substitutes: "claiming success from a check's last line or exit status alone; a change outside the listed files; a commit without the saved check output"
  boundaries: "only these files: practice/PROBLEM.md, practice/cases.json, practice/grade.py, practice/reference/solution.py, tests/test_practice.py; no irreversible action and no spend; Brian's request as quoted is the scope"
  done_when: "uv run pytest -v tests/test_practice.py shows the reference passing and a broken refund rule failing The check's full output is committed as docs/plans/kit-v2-practice.check.txt, and the commit is tagged [Goal kit-v2-practice] with an Asked: line quoting the request."
  do_not_gate_on: "Brian's review of the plan page; work outside the listed files"
---

# Add a 2-hour practice problem with a known-answer grader

## When a run fails or surprises us

Preserve the failed check and its execution trace id. Before selecting a fix,
read the complete inputs, prompts, tool arguments/results, intermediate stages
and final output, including the full check command/output and the changed files.
Cite the observed divergence and classify evidence absent, returned but unused
or contradicted, invalid expectation, or unresolved. Investigate an unresolved
cause before authorizing a causal repair. Bind the targeted repair to a new
traced verification run; retain the failed original. Review every failing or
surprising item and a sample of passes. A complete review is distinct from a
passing run. Criterion `outcome` covers the entire requested success check.

## Actor and result

**Actor:** Brian, who asked for this change.

**Request (verbatim):** Brian 2026-10-11 set /goal "make interview-kit ready for a timed agentic-AI take-home in a hosted IDE whose only allowed AI is its own recorded chat"

**Desired result:** practice/ holds a spec, data, known-answer cases and a grader; a hidden reference passes and a broken one fails

**Stable example:** python practice/grade.py with the reference solution prints 7/7 cases PASS

## Authority and non-goals

**Authority:** Brian asked for this change in his own repository; one agent makes it.

**Non-goals:** nothing outside the files listed under Vertical and reset. No irreversible action and no spend.

## Requirements

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | practice/ holds a spec, data, known-answer cases and a grader; a hidden reference passes and a broken one fails | asked: Brian 2026-10-11 set /goal "make interview-kit ready for a timed agentic-AI take-home in a hosted IDE whose only allowed AI is its own recorded chat" | the success check under Success and disproof, its output saved as `docs/plans/kit-v2-practice.check.txt` | planned, not yet run |

Requirements the change's own claims imply: none beyond R1; the change presents nothing as following a standard, schema or contract.

## Success and disproof

**Success evidence:** uv run pytest -v tests/test_practice.py shows the reference passing and a broken refund rule failing

**Trace review:** the run whose full trace is judged is the success check above, run once on the commit that makes the change; no model, agent or LLM pipeline runs under this plan. Where the trace lives: the check's complete output, with the exact command and its exit status, is saved as `docs/plans/kit-v2-practice.check.txt` and committed with the change. What must be seen in it beyond the final result: the command ran against the files listed under Vertical and reset at that commit, each check or test it reports appears by name with its result and none is skipped, and the exit status matches; for each model element listed under System model, the output shows what that line says. Success and disproof are both judged from that file.

**Disproof:** the broken-rule test passes, i.e. the grader cannot fail

## System model

**System model:** `wiki/index.md`

**Model elements this change adds, changes or relies on, and what the saved check output must show of each:**

- practice problem (goal item 5)

## Capability reuse

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because this is content inside a standalone public interview kit, not a cross-project mechanism

## Uncertainties

| Uncertainty | Owner or resolving evidence |
| --- | --- |
| Whether the change needs files beyond the list below; if so it is out of scope for this plan | Resolved before editing: git status --short lists only: practice/PROBLEM.md practice/cases.json practice/grade.py practice/reference/solution.py tests/test_practice.py |

## Vertical and reset

One vertical over these files (and the saved check output, `docs/plans/kit-v2-practice.check.txt`):

- `practice/PROBLEM.md`
- `practice/cases.json`
- `practice/grade.py`
- `practice/reference/solution.py`
- `tests/test_practice.py`

The vertical delivers: practice/ holds a spec, data, known-answer cases and a grader; a hidden reference passes and a broken one fails It is done when this holds: uv run pytest -v tests/test_practice.py shows the reference passing and a broken refund rule failing

Make the change, run the success check, commit. Reset: `git revert` of the commit. Not pursued: anything outside these files.

## Activation facts

No shared mechanism, no comparison, no LLM at the centre, no irreversible action or spend, and no claim to follow an external standard: a bounded change Brian asked for.
