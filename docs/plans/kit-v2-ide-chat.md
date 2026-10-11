---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v2-ide-chat
plan_id: kit-v2-ide-chat
status: proposed
planning_path: requested
method_conformance_receipt: docs/plans/kit-v2-ide-chat.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "skills/using-ide-ai-chat explains Ask/Plan/Edit use, model choice, clone-not-paste and graded failure patterns, and is in KIT.md, README and wiki"
  canonical_example: "KIT.md contains the heading 'Skill: use the IDE's AI chat so the recording shows judgment'"
  forbidden_substitutes: "claiming success from a check's last line or exit status alone; a change outside the listed files; a commit without the saved check output"
  boundaries: "only these files: skills/using-ide-ai-chat/SKILL.md, KIT.md, README.md, wiki/index.md; no irreversible action and no spend; the owner's request as quoted is the scope"
  done_when: "grep finds the skill heading in KIT.md and its row in README.md and wiki/index.md The check's full output is committed as docs/plans/kit-v2-ide-chat.check.txt, and the commit is tagged [Goal kit-v2-ide-chat] with an Asked: line quoting the request."
  do_not_gate_on: "the owner's review of the plan page; work outside the listed files"
---

# IDE AI-chat skill

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

**Actor:** The owner, who asked for this change.

**Request (verbatim):** The owner 2026-10-11 set /goal "make interview-kit ready for a timed agentic-AI take-home in a hosted IDE whose only allowed AI is its own recorded chat"

**Desired result:** skills/using-ide-ai-chat explains Ask/Plan/Edit use, model choice, clone-not-paste and graded failure patterns, and is in KIT.md, README and wiki

**Stable example:** KIT.md contains the heading 'Skill: use the IDE's AI chat so the recording shows judgment'

## Authority and non-goals

**Authority:** the owner asked for this change in his own repository; one agent makes it.

**Non-goals:** nothing outside the files listed under Vertical and reset. No irreversible action and no spend.

## Requirements

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | skills/using-ide-ai-chat explains Ask/Plan/Edit use, model choice, clone-not-paste and graded failure patterns, and is in KIT.md, README and wiki | asked: The owner 2026-10-11 set /goal "make interview-kit ready for a timed agentic-AI take-home in a hosted IDE whose only allowed AI is its own recorded chat" | the success check under Success and disproof, its output saved as `docs/plans/kit-v2-ide-chat.check.txt` | planned, not yet run |

Requirements the change's own claims imply: none beyond R1; the change presents nothing as following a standard, schema or contract.

## Success and disproof

**Success evidence:** grep finds the skill heading in KIT.md and its row in README.md and wiki/index.md

**Trace review:** the run whose full trace is judged is the success check above, run once on the commit that makes the change; no model, agent or LLM pipeline runs under this plan. Where the trace lives: the check's complete output, with the exact command and its exit status, is saved as `docs/plans/kit-v2-ide-chat.check.txt` and committed with the change. What must be seen in it beyond the final result: the command ran against the files listed under Vertical and reset at that commit, each check or test it reports appears by name with its result and none is skipped, and the exit status matches; for each model element listed under System model, the output shows what that line says. Success and disproof are both judged from that file.

**Disproof:** The skill is missing from KIT.md after ./build_kit.sh, or cites an unsourced claim

## System model

**System model:** `wiki/index.md`

**Model elements this change adds, changes or relies on, and what the saved check output must show of each:**

- none -- documentation only; no running model element

## Capability reuse

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because this is content inside a standalone public interview kit, not a cross-project mechanism

## Uncertainties

| Uncertainty | Owner or resolving evidence |
| --- | --- |
| Whether the change needs files beyond the list below; if so it is out of scope for this plan | Resolved before editing: git status --short lists only: skills/using-ide-ai-chat/SKILL.md KIT.md README.md wiki/index.md |

## Vertical and reset

One vertical over these files (and the saved check output, `docs/plans/kit-v2-ide-chat.check.txt`):

- `skills/using-ide-ai-chat/SKILL.md`
- `KIT.md`
- `README.md`
- `wiki/index.md`

The vertical delivers: skills/using-ide-ai-chat explains Ask/Plan/Edit use, model choice, clone-not-paste and graded failure patterns, and is in KIT.md, README and wiki It is done when this holds: grep finds the skill heading in KIT.md and its row in README.md and wiki/index.md

Make the change, run the success check, commit. Reset: `git revert` of the commit. Not pursued: anything outside these files.

## Activation facts

No shared mechanism, no comparison, no LLM at the centre, no irreversible action or spend, and no claim to follow an external standard: a bounded change the owner asked for.
