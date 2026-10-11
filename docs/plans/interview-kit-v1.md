---
schema_version: "1.0"
artifact_type: design_plan
id: interview-kit-v1
plan_id: interview-kit-v1
status: proposed
planning_path: requested
method_conformance_receipt: docs/plans/interview-kit-v1.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "A public GitHub repo holds working rules, skill guides and an agent template that a fresh environment pulls in with one command, plus a single KIT.md to paste when offline; single-agent work with no coordination ceremony (no claims, worktrees or work-unit graph), which is a non-goal"
  canonical_example: "git clone --depth 1 <this repo's URL> kit in an empty folder yields AGENTS.md, skills/ and examples/agent_template.py."
  forbidden_substitutes: "claiming success from a check's last line or exit status alone; a change outside the listed files; a commit without the saved check output"
  boundaries: "only these files: AGENTS.md, skills, examples, tests, README.md; no irreversible action and no spend; the owner's request as quoted is the scope"
  done_when: "On a clean clone made from GitHub without login, the saved check output docs/plans/interview-kit-v1.check.txt shows: (1) ls listing AGENTS.md, KIT.md, the three skills/*.md files and examples/agent_template.py; (2) uv run pytest -v listing test_tool_result_reaches_the_model, test_tool_error_is_returned_not_raised and test_no_tool_needed_ends_immediately as PASSED, which assert the exact tool output 'Order A-100: shipped' and the error text 'Unknown order id' using a scripted fake model; (3) curl of the raw KIT.md URL without login returning text containing 'Working rules for the coding assistant'; (4) gitleaks --no-git and a grep for emails and phone numbers finding nothing; (5) a light LLM read (OpenRouter) of the full text of every committed file asked to list any personal detail of a real person, client or employer material, private message, or non-public record, with its verbatim answer saved; pass only if it lists none. Trace exemption: no model, agent or pipeline under test runs, so the check output is the whole trace. The trace-debugging procedure is distinct from the anticipated failure modes named under disproof, and review completeness (every check's output read) is judged separately from the run verdict. The check's full output is committed as docs/plans/interview-kit-v1.check.txt, and the commit is tagged [Goal interview-kit-v1] with an Asked: line quoting the request."
  do_not_gate_on: "the owner's review of the plan page; work outside the listed files"
---

# Portable best-practice kit for hosted coding tests

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

**Request (verbatim):** The owner 2026-10-10 "im talking about bringing in what is essentialy best practices docuemtnation" so that he can "put them on github and then pull them in right away"

**Desired result:** A public GitHub repo holds working rules, skill guides and an agent template that a fresh environment pulls in with one command, plus a single KIT.md to paste when offline; single-agent work with no coordination ceremony (no claims, worktrees or work-unit graph), which is a non-goal.

**Stable example:** git clone --depth 1 <this repo's URL> kit in an empty folder yields AGENTS.md, skills/ and examples/agent_template.py.

## Authority and non-goals

**Authority:** the owner asked for this change in his own repository; one agent makes it.

**Non-goals:** nothing outside the files listed under Vertical and reset. No irreversible action and no spend.

## Requirements

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | A public GitHub repo holds working rules, skill guides and an agent template that a fresh environment pulls in with one command, plus a single KIT.md to paste when offline; single-agent work with no coordination ceremony (no claims, worktrees or work-unit graph), which is a non-goal. | asked: The owner 2026-10-10 "im talking about bringing in what is essentialy best practices docuemtnation" so that he can "put them on github and then pull them in right away" | the success check under Success and disproof, its output saved as `docs/plans/interview-kit-v1.check.txt` | planned, not yet run |
| R2 | README.md lists every committed note and example file in its table | stated with the request | the check output compares git ls-files with the README table | planned, not yet run |
| R3 | KIT.md equals the output of build_kit.sh | stated with the request | the check output reruns build_kit.sh then git diff --exit-code KIT.md with exit 0 | planned, not yet run |

Requirements the change's own claims imply are listed above as R2 onward.

## Success and disproof

**Success evidence:** On a clean clone made from GitHub without login, the saved check output docs/plans/interview-kit-v1.check.txt shows: (1) ls listing AGENTS.md, KIT.md, the three skills/*.md files and examples/agent_template.py; (2) uv run pytest -v listing test_tool_result_reaches_the_model, test_tool_error_is_returned_not_raised and test_no_tool_needed_ends_immediately as PASSED, which assert the exact tool output 'Order A-100: shipped' and the error text 'Unknown order id' using a scripted fake model; (3) curl of the raw KIT.md URL without login returning text containing 'Working rules for the coding assistant'; (4) gitleaks --no-git and a grep for emails and phone numbers finding nothing; (5) a light LLM read (OpenRouter) of the full text of every committed file asked to list any personal detail of a real person, client or employer material, private message, or non-public record, with its verbatim answer saved; pass only if it lists none. Trace exemption: no model, agent or pipeline under test runs, so the check output is the whole trace. The trace-debugging procedure is distinct from the anticipated failure modes named under disproof, and review completeness (every check's output read) is judged separately from the run verdict.

**Trace review:** the run whose full trace is judged is the success check above, run once on the commit that makes the change; no model, agent or LLM pipeline runs under this plan. Where the trace lives: the check's complete output, with the exact command and its exit status, is saved as `docs/plans/interview-kit-v1.check.txt` and committed with the change. What must be seen in it beyond the final result: the command ran against the files listed under Vertical and reset at that commit, each check or test it reports appears by name with its result and none is skipped, and the exit status matches; for each model element listed under System model, the output shows what that line says. Success and disproof are both judged from that file.

**Disproof:** The clone or raw URL needs a login, any of the three named tests fails or is skipped on the clean clone, or any file contains a secret, personal detail or non-public material.

## System model

System model: exempt -- documentation repo with no stored state, no service and no user-facing view, so no source-linked views apply

## Capability reuse

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because the need is notes readable by a third-party hosted IDE's own assistant with no access to the workspace; the workspace skills repo (agent-skills) is tied to local paths and policies and cannot be used there

## Uncertainties

| Uncertainty | Owner or resolving evidence |
| --- | --- |
| Whether the change needs files beyond the list below; if so it is out of scope for this plan | Resolved before editing: the repository is new and empty apart from this change, so git ls-files after the commit is the complete scope: AGENTS.md, README.md, build_kit.sh, KIT.md, skills/, examples/, tests/, pyproject.toml, uv.lock, .gitignore; nothing outside this repository is touched |

## Vertical and reset

One vertical over these files (and the saved check output, `docs/plans/interview-kit-v1.check.txt`):

- `AGENTS.md`
- `skills`
- `examples`
- `tests`
- `README.md`

The vertical delivers: A public GitHub repo holds working rules, skill guides and an agent template that a fresh environment pulls in with one command, plus a single KIT.md to paste when offline; single-agent work with no coordination ceremony (no claims, worktrees or work-unit graph), which is a non-goal. It is done when this holds: On a clean clone made from GitHub without login, the saved check output docs/plans/interview-kit-v1.check.txt shows: (1) ls listing AGENTS.md, KIT.md, the three skills/*.md files and examples/agent_template.py; (2) uv run pytest -v listing test_tool_result_reaches_the_model, test_tool_error_is_returned_not_raised and test_no_tool_needed_ends_immediately as PASSED, which assert the exact tool output 'Order A-100: shipped' and the error text 'Unknown order id' using a scripted fake model; (3) curl of the raw KIT.md URL without login returning text containing 'Working rules for the coding assistant'; (4) gitleaks --no-git and a grep for emails and phone numbers finding nothing; (5) a light LLM read (OpenRouter) of the full text of every committed file asked to list any personal detail of a real person, client or employer material, private message, or non-public record, with its verbatim answer saved; pass only if it lists none. Trace exemption: no model, agent or pipeline under test runs, so the check output is the whole trace. The trace-debugging procedure is distinct from the anticipated failure modes named under disproof, and review completeness (every check's output read) is judged separately from the run verdict.

Make the change, run the success check, commit. Reset: `git revert` of the commit. Not pursued: anything outside these files.

## Activation facts

No shared mechanism, no comparison, no LLM at the centre, no irreversible action or spend, and no claim to follow an external standard: a bounded change the owner asked for.
