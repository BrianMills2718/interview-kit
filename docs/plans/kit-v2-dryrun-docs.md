---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v2-dryrun-docs
plan_id: kit-v2-dryrun-docs
status: proposed
planning_path: requested
method_conformance_receipt: docs/plans/kit-v2-dryrun-docs.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "The kit's notes answer the questions the timed dry run got stuck on: setup, approval in a recorded chat, version checks in a uv venv, two langgraph traps, the provider key"
  canonical_example: "A candidate reading PROBLEM.md knows to install langchain langgraph pytest and not to open cases.json first"
  forbidden_substitutes: "claiming success from a check's last line or exit status alone; a change outside the listed files; a commit without the saved check output"
  boundaries: "only these files: AGENTS.md, practice/PROBLEM.md, skills/langgraph-agent/SKILL.md, skills/plan/SKILL.md, skills/using-ide-ai-chat/SKILL.md; no irreversible action and no spend; Brian's request as quoted is the scope"
  done_when: "uv run pytest -v passes; the two new watchlist rows reproduce on langgraph 1.2.14 The check's full output is committed as docs/plans/kit-v2-dryrun-docs.check.txt, and the commit is tagged [Goal kit-v2-dryrun-docs] with an Asked: line quoting the request."
  do_not_gate_on: "Brian's review of the plan page; work outside the listed files"
---

# Fold the dry run's documentation frictions into the kit

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

**Desired result:** The kit's notes answer the questions the timed dry run got stuck on: setup, approval in a recorded chat, version checks in a uv venv, two langgraph traps, the provider key

**Stable example:** A candidate reading PROBLEM.md knows to install langchain langgraph pytest and not to open cases.json first

## Authority and non-goals

**Authority:** Brian asked for this change in his own repository; one agent makes it.

**Non-goals:** nothing outside the files listed under Vertical and reset. No irreversible action and no spend.

## Requirements

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | The kit's notes answer the questions the timed dry run got stuck on: setup, approval in a recorded chat, version checks in a uv venv, two langgraph traps, the provider key | asked: Brian 2026-10-11 set /goal "make interview-kit ready for a timed agentic-AI take-home in a hosted IDE whose only allowed AI is its own recorded chat" | the success check under Success and disproof, its output saved as `docs/plans/kit-v2-dryrun-docs.check.txt` | planned, not yet run |

Requirements the change's own claims imply: none beyond R1; the change presents nothing as following a standard, schema or contract.

## Success and disproof

**Success evidence:** uv run pytest -v passes; the two new watchlist rows reproduce on langgraph 1.2.14

**Trace review:** the run whose full trace is judged is the success check above, run once on the commit that makes the change; no model, agent or LLM pipeline runs under this plan. Where the trace lives: the check's complete output, with the exact command and its exit status, is saved as `docs/plans/kit-v2-dryrun-docs.check.txt` and committed with the change. What must be seen in it beyond the final result: the command ran against the files listed under Vertical and reset at that commit, each check or test it reports appears by name with its result and none is skipped, and the exit status matches; for each model element listed under System model, the output shows what that line says. Success and disproof are both judged from that file.

**Disproof:** Command(resume=None) works or an interrupted node runs once on langgraph 1.2.14

## System model

**System model:** `wiki/index.md`

**Model elements this change adds, changes or relies on, and what the saved check output must show of each:**

- practice problem and skills

## Capability reuse

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because this is content inside a standalone public interview kit, not a cross-project mechanism

## Uncertainties

| Uncertainty | Owner or resolving evidence |
| --- | --- |
| Whether the change needs files beyond the list below; if so it is out of scope for this plan | Resolved before editing: git status --short lists only: AGENTS.md practice/PROBLEM.md skills/langgraph-agent/SKILL.md skills/plan/SKILL.md skills/using-ide-ai-chat/SKILL.md |

## Vertical and reset

One vertical over these files (and the saved check output, `docs/plans/kit-v2-dryrun-docs.check.txt`):

- `AGENTS.md`
- `practice/PROBLEM.md`
- `skills/langgraph-agent/SKILL.md`
- `skills/plan/SKILL.md`
- `skills/using-ide-ai-chat/SKILL.md`

The vertical delivers: The kit's notes answer the questions the timed dry run got stuck on: setup, approval in a recorded chat, version checks in a uv venv, two langgraph traps, the provider key It is done when this holds: uv run pytest -v passes; the two new watchlist rows reproduce on langgraph 1.2.14

Make the change, run the success check, commit. Reset: `git revert` of the commit. Not pursued: anything outside these files.

## Activation facts

No shared mechanism, no comparison, no LLM at the centre, no irreversible action or spend, and no claim to follow an external standard: a bounded change Brian asked for.
