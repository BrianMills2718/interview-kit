---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v2-watchlist
plan_id: kit-v2-watchlist
status: proposed
planning_path: requested
method_conformance_receipt: docs/plans/kit-v2-watchlist.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "skills/langgraph-agent has a watchlist table mapping old API forms to current ones, each row naming the package version it was checked against, and points to the new patterns"
  canonical_example: "The row for create_react_agent cites the LangGraphDeprecatedSinceV10 warning seen on langgraph 1.2.14"
  forbidden_substitutes: "claiming success from a check's last line or exit status alone; a change outside the listed files; a commit without the saved check output"
  boundaries: "only these files: skills/langgraph-agent/SKILL.md, KIT.md, wiki/index.md; no irreversible action and no spend; Brian's request as quoted is the scope"
  done_when: "every watchlist row has a version in its last column and KIT.md contains the table The check's full output is committed as docs/plans/kit-v2-watchlist.check.txt, and the commit is tagged [Goal kit-v2-watchlist] with an Asked: line quoting the request."
  do_not_gate_on: "Brian's review of the plan page; work outside the listed files"
---

# Version-checked deprecated-API watchlist

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

**Desired result:** skills/langgraph-agent has a watchlist table mapping old API forms to current ones, each row naming the package version it was checked against, and points to the new patterns

**Stable example:** The row for create_react_agent cites the LangGraphDeprecatedSinceV10 warning seen on langgraph 1.2.14

## Authority and non-goals

**Authority:** Brian asked for this change in his own repository; one agent makes it.

**Non-goals:** nothing outside the files listed under Vertical and reset. No irreversible action and no spend.

## Requirements

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | skills/langgraph-agent has a watchlist table mapping old API forms to current ones, each row naming the package version it was checked against, and points to the new patterns | asked: Brian 2026-10-11 set /goal "make interview-kit ready for a timed agentic-AI take-home in a hosted IDE whose only allowed AI is its own recorded chat" | the success check under Success and disproof, its output saved as `docs/plans/kit-v2-watchlist.check.txt` | planned, not yet run |

Requirements the change's own claims imply: none beyond R1; the change presents nothing as following a standard, schema or contract.

## Success and disproof

**Success evidence:** every watchlist row has a version in its last column and KIT.md contains the table

**Trace review:** the run whose full trace is judged is the success check above, run once on the commit that makes the change; no model, agent or LLM pipeline runs under this plan. Where the trace lives: the check's complete output, with the exact command and its exit status, is saved as `docs/plans/kit-v2-watchlist.check.txt` and committed with the change. What must be seen in it beyond the final result: the command ran against the files listed under Vertical and reset at that commit, each check or test it reports appears by name with its result and none is skipped, and the exit status matches; for each model element listed under System model, the output shows what that line says. Success and disproof are both judged from that file.

**Disproof:** A row states behaviour not reproduced against the installed package

## System model

**System model:** `wiki/index.md`

**Model elements this change adds, changes or relies on, and what the saved check output must show of each:**

- none -- documentation only

## Capability reuse

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because this is content inside a standalone public interview kit, not a cross-project mechanism

## Uncertainties

| Uncertainty | Owner or resolving evidence |
| --- | --- |
| Whether the change needs files beyond the list below; if so it is out of scope for this plan | Resolved before editing: git status --short lists only: skills/langgraph-agent/SKILL.md KIT.md wiki/index.md |

## Vertical and reset

One vertical over these files (and the saved check output, `docs/plans/kit-v2-watchlist.check.txt`):

- `skills/langgraph-agent/SKILL.md`
- `KIT.md`
- `wiki/index.md`

The vertical delivers: skills/langgraph-agent has a watchlist table mapping old API forms to current ones, each row naming the package version it was checked against, and points to the new patterns It is done when this holds: every watchlist row has a version in its last column and KIT.md contains the table

Make the change, run the success check, commit. Reset: `git revert` of the commit. Not pursued: anything outside these files.

## Activation facts

No shared mechanism, no comparison, no LLM at the centre, no irreversible action or spend, and no claim to follow an external standard: a bounded change Brian asked for.
