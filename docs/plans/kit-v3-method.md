---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v3-method
plan_id: kit-v3-method
status: proposed
planning_path: requested
method_conformance_receipt: docs/plans/kit-v3-method.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "A method/ folder holds the system model, architecture views, design chain, decision rules, AES setup and diagram guidance, adapted from the owner's own company-planning, AES and representation-router repos, and the kit gets its own one-page system model built with it. AES is the owner's own planning CLI used as a tool at a pinned revision; nothing here claims conformance to an external standard"
  canonical_example: "In a fresh clone, kit/method/README.md says which method file to use at each stage of a timed test, and bash kit/method/install_aes.sh then aes plan validate kit/method/aes-plan.example.yaml exits 0"
  forbidden_substitutes: "claiming success from a check's last line or exit status alone; a change outside the listed files; a commit without the saved check output"
  boundaries: "only these files: method, tests, docs, wiki/index.md; no irreversible action and no spend; the owner's request as quoted is the scope"
  done_when: "(1) tests/test_method.py runs 'aes plan validate' on method/aes-plan.example.yaml and asserts exit 0 and the word VALID, which tests the property that the shipped AES plan template is accepted by the pinned AES revision; it also asserts every method/*.md file is linked from method/README.md, which tests that the index reaches every method file; (2) tests/test_model.py asserts the model's runtime rows P1-P4 equal the checked writers and each writer file contains its write (e.g. build_kit.sh contains '> KIT.md'), and that KIT.md equals a fresh build, which tests model-to-code agreement in both directions; (3) tests/test_wiki_map.py asserts every relative link in wiki/index.md resolves, which tests the map matches the files; (4) gitleaks detect --no-git on method/ exits 0 and grep -riE 'inside success|istv|<owner-username>' method/ returns no lines, which tests 'no secrets, owner username or Inside Success branding in the new files' The check's full output on the parent commit and on the change commit is committed as docs/plans/kit-v3-method.check.txt, and the commit is tagged [Goal kit-v3-method] with an Asked: line quoting the request."
  do_not_gate_on: "the owner's review of the plan page; work outside the listed files"
---

# Bring the owner's planning method into the kit

## When a run fails or surprises us

This procedure is separate from the anticipated failure named in the disproof
under Success and disproof: it applies to any run that fails or surprises us.
Preserve the failed check and its execution trace id. Before selecting a fix,
read the complete inputs, prompts, tool arguments/results, intermediate stages
and final output, including the full check command/output and the changed files.
Cite the observed divergence and classify evidence absent, returned but unused
or contradicted, invalid expectation, or unresolved. An unresolved diagnosis
cannot authorize a causal repair; it permits only further investigation. Bind the targeted repair to a new
traced verification run; retain the failed original. Review every failing or
surprising item and a sample of passes. A complete review is distinct from a
passing run. Criterion `outcome` covers the entire requested success check.

## Actor and result

**Actor:** the owner, who asked for this change.

**Request (verbatim):** The owner 2026-10-11 "what i want is the planning mehtodology all the models and stuff"

**Desired result:** A method/ folder holds the system model, architecture views, design chain, decision rules, AES setup and diagram guidance, adapted from the owner's own company-planning, AES and representation-router repos, and the kit gets its own one-page system model built with it. AES is the owner's own planning CLI used as a tool at a pinned revision; nothing here claims conformance to an external standard

**Stable example:** In a fresh clone, kit/method/README.md says which method file to use at each stage of a timed test, and bash kit/method/install_aes.sh then aes plan validate kit/method/aes-plan.example.yaml exits 0

## Authority and non-goals

**Authority:** the owner asked for this change in his own repository; one agent makes it.

**Non-goals:** nothing outside the files listed under Vertical and reset. No irreversible action and no spend.

## Requirements

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | A method/ folder holds the system model, architecture views, design chain, decision rules, AES setup and diagram guidance, adapted from the owner's own company-planning, AES and representation-router repos, and the kit gets its own one-page system model built with it. AES is the owner's own planning CLI used as a tool at a pinned revision; nothing here claims conformance to an external standard | asked: The owner 2026-10-11 "what i want is the planning mehtodology all the models and stuff" | the success check under Success and disproof, its output saved as `docs/plans/kit-v3-method.check.txt` | planned, not yet run |

Requirements the change's own claims imply: none beyond R1; the change presents nothing as following a standard, schema or contract.

## Success and disproof

**Success evidence:** (1) tests/test_method.py runs 'aes plan validate' on method/aes-plan.example.yaml and asserts exit 0 and the word VALID, which tests the property that the shipped AES plan template is accepted by the pinned AES revision; it also asserts every method/*.md file is linked from method/README.md, which tests that the index reaches every method file; (2) tests/test_model.py asserts the model's runtime rows P1-P4 equal the checked writers and each writer file contains its write (e.g. build_kit.sh contains '> KIT.md'), and that KIT.md equals a fresh build, which tests model-to-code agreement in both directions; (3) tests/test_wiki_map.py asserts every relative link in wiki/index.md resolves, which tests the map matches the files; (4) gitleaks detect --no-git on method/ exits 0 and grep -riE 'inside success|istv|<owner-username>' method/ returns no lines, which tests 'no secrets, owner username or Inside Success branding in the new files'

**Trace review:** two runs of the success check above are judged from their full output: one on the parent commit before the change (the disproof run: it must show the defect or the check failing, which proves the check can fail) and one on the commit that makes the change (the success run); no model, agent or LLM pipeline runs under this plan. Where the trace lives: the check's complete output, with the exact command and its exit status, is saved as `docs/plans/kit-v3-method.check.txt` and committed with the change. What must be seen in it beyond the final result: the command ran against the files listed under Vertical and reset at that commit, each check or test it reports appears by name with its result and none is skipped, and the exit status matches; for each model element listed under System model, the output shows what that line says. Both runs are saved in that one file, each headed by its commit: the disproof condition is judged from both (it holds if the success run still shows the defect, or if the before run already passes, meaning the check cannot detect it), and success from the success run.

**Disproof:** aes plan validate rejects the example plan, or a method file is not linked from method/README.md, or test_model finds a model row without its writer, or a method file contains secrets, the owner's username or Inside Success branding

## System model

**System model:** `docs/model/ARCHITECTURE.md`, a file in this repository describing this repository only (not a shared model). Reachable from the documentation entry point `wiki/index.md`, which links `docs/model/ARCHITECTURE.md`.

**Model elements this change adds, changes or relies on, and what the saved check output must show of each:**

- P3 'install AES' (writer method/install_aes.sh, writes the aes uv tool): added; the saved check output must show test_every_runtime_row_has_a_writer_that_writes_it failing before (install_aes.sh missing) and passing after. V1 KIT.md: changes to include method/; the output must show test_kit_md_matches_its_sources passing. V4 wiki/index.md: gains the System model and Method rows and decision 8; the output must show test_every_wiki_link_resolves passing

**Views, freshness and reconciliation:** the applicable view is the requirement-to-verification link in the Requirements table (each requirement and the check that shows it, the check being source-linked by its command); no other view applies because the change adds, changes or relies on no entity, process, record, event or view beyond the elements listed above. Freshness: the model's drift test (`tests/test_model.py`, `tests/test_check_sh.py`, `tests/test_practice.py`, `tests/test_wiki_map.py`) runs inside the success check and its output is in the saved check file. If an element above is added, removed or renamed, the model, its view coverage and the saved check output are reconciled in the same commit, and otherwise the model needs no update because the elements keep their meaning.

## Capability reuse

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because this is content inside a standalone public interview kit, not a cross-project mechanism
- What the work needs that no entry provides: edits to this repository's own files (`method`, `tests`, `docs`, `wiki/index.md`); catalogue entries are cross-project capabilities, and none edits a repository's own source.

## Uncertainties

Material uncertainties. This one is the complete set; it is material because a file outside the list would
make the change exceed this plan's scope.

| Material uncertainty | Owner or resolving evidence |
| --- | --- |
| Whether the change needs files beyond the list below; if so it is out of scope for this plan | Resolved before editing: git status --short lists only: method tests docs wiki/index.md |

## Vertical and reset

One vertical over these files (and the saved check output, `docs/plans/kit-v3-method.check.txt`):

- `method`
- `tests`
- `docs`
- `wiki/index.md`

The vertical delivers: A method/ folder holds the system model, architecture views, design chain, decision rules, AES setup and diagram guidance, adapted from the owner's own company-planning, AES and representation-router repos, and the kit gets its own one-page system model built with it. AES is the owner's own planning CLI used as a tool at a pinned revision; nothing here claims conformance to an external standard It is done when this holds: (1) tests/test_method.py runs 'aes plan validate' on method/aes-plan.example.yaml and asserts exit 0 and the word VALID, which tests the property that the shipped AES plan template is accepted by the pinned AES revision; it also asserts every method/*.md file is linked from method/README.md, which tests that the index reaches every method file; (2) tests/test_model.py asserts the model's runtime rows P1-P4 equal the checked writers and each writer file contains its write (e.g. build_kit.sh contains '> KIT.md'), and that KIT.md equals a fresh build, which tests model-to-code agreement in both directions; (3) tests/test_wiki_map.py asserts every relative link in wiki/index.md resolves, which tests the map matches the files; (4) gitleaks detect --no-git on method/ exits 0 and grep -riE 'inside success|istv|<owner-username>' method/ returns no lines, which tests 'no secrets, owner username or Inside Success branding in the new files'

Make the change, run the success check before and after it, commit. Reset: `git revert` of the commit. Not pursued: anything outside these files. This plan adds no coordinated-work ceremony: no work-unit graph, no review or release contract, no claim beyond the repository's own rules.

## Activation facts

Each fact, with its value and why:

- `shared_mechanism`: false -- the change edits only the listed files and adds no contract, algorithm or mechanism other code uses.
- `empirical_comparison_proposed`: false -- no alternatives are compared; the success check verifies the one change.
- `llm_central`: false -- the change makes no model call.
- `irreversible_or_spend_action`: false -- the change is reverted by `git revert` and spends nothing.
- `claims_external_standard`: false -- the work claims no external standard, schema or contract.
- `aes_governed_target`: false -- this repository has no `.aes/target.yaml` (checked by quick-adopt).
- `durable_documents_declared`: false -- `.agentic/repo.yaml` declares no `durable_documents` (checked by quick-adopt).

