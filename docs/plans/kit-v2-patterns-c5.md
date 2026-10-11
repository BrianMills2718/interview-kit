---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v2-patterns-c5
status: proposed
method_conformance_receipt: docs/plans/kit-v2-patterns-c5.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "A candidate in a hosted Python IDE pulls the kit and can copy a tested supervisor-with-specialists pattern, a tested streaming pattern, a tested MCP server, and a one-page sourced MCP/A2A note."
  canonical_example: "In a fresh clone with no API key, uv run pytest -v lists test_supervisor_routes_to_the_right_specialist_and_uses_its_answer PASSED, and KIT.md contains the section Several agents: a supervisor with specialists as tools."
  forbidden_substitutes: "Snippets no test runs; tests that still pass with the pattern broken; API names recalled from memory rather than checked against current docs and the installed packages."
  boundaries: "Only interview-kit, only the files agreed with session code-c7 (examples/patterns_multi.py, examples/mcp_server.py, their tests, skills/mcp-and-a2a, sections after Pitfalls in skills/langgraph-agent, KIT.md, wiki, README rows); public repo, so no company names, interview details, personal data or secrets; no live or paid LLM calls."
  done_when: "docs/plans/kit-v2-patterns-c5.check.txt (full pytest -v, build_kit, plugin validate, privacy grep) and docs/plans/mutation.txt show the five new tests PASSED by name, each broken pattern failing its test, KIT.md at or under 600 lines, plugin validate passing and no private-data hits."
  do_not_gate_on: "The IDE AI chat (needs an account), the real test environment, code-c7 items (watchlist, structured output, retrieval, interrupt, practice problem, dry run), the owner reading it."
---

# Kit v2: supervisor and streaming patterns, MCP server, MCP/A2A note

Each section below answers the checklist items quoted in it; the gate judges only that
section's text. Replace every `TODO(answer ...)` line before running `cli.py check`. Quote
values in the front matter: an unquoted ` #` starts a YAML comment and cuts the value.

## Actor and result

> **CORE-ACTOR-RESULT-EXAMPLE** (blocking): The plan names the actor it serves, the desired result, and one stable, concrete, user-visible example of that result.

**Actor:** a candidate in a timed agentic-AI take-home in a hosted Python IDE where only the IDE's own recorded AI chat is allowed. **Result:** after `git clone` they can copy (1) a supervisor that delegates to specialist agents wrapped as tools, (2) a streaming helper that shows each step, (3) an MCP server exposing a tool, each with an offline test, plus (4) a one-page note on MCP and A2A with the facts checked against the current specs. **Example:** with no API key, `uv run pytest -v` in a fresh clone lists `tests/test_patterns_multi.py::test_supervisor_routes_to_the_right_specialist_and_uses_its_answer PASSED`.

## Requirements

> **CORE-REQUIREMENTS-TRACED** (blocking): The plan lists its requirements: what was asked for, and what the delivered work's own claims imply. A claim here is what the work is presented as being or doing to its users, for example work presented as following a standard, schema or contract (which implies conformance to it) or an output labelled as showing something (which implies it shows it correctly); the plan's own format and front matter are not such claims, and the details a check examines (what a trace must show) belong to that check rather than being separate requirements. Each requirement names the check that verifies it (a test, script, gate step, or named review of a run) and its status: passing, failing, planned and not yet run, or deferred with a stated reason; deferred requirements are carried onto every release or completion record the plan names. A plan fails this item if it has no requirements list, if any requirement has neither a check nor an explicit deferral with its reason, or if the plan presents the work as following a named standard, schema or contract, or as having another property its users rely on, that its requirements list omits.

| # | Requirement (source) | Check | Status |
|---|---|---|---|
| R1 | Supervisor pattern with an offline test (asked: /goal item 2) | `test_supervisor_routes_to_the_right_specialist_and_uses_its_answer`, `test_supervisor_can_ask_two_specialists_in_turn` PASSED in check.txt | passing (worktree run) |
| R2 | Streaming pattern with an offline test (asked: /goal item 2) | `test_stream_yields_each_step_in_order` PASSED | passing (worktree run) |
| R3 | APIs match current docs (asked: "checked against the current API (context7)") | context7 /langchain-ai/langgraph Pregel.stream stream_mode docs; MCP SDK source in the installed mcp 2.3.0; tests import the installed packages | passing |
| R4 | Tests could fail (workspace rule) | docs/plans/mutation.txt: three mutations, each makes its test FAIL | passing |
| R5 | Short, accurate MCP/A2A note (asked: /goal item 3) | each claim traced to the MCP spec 2026-07-28 pages, the A2A spec 1.0.0 page or the installed SDK, fetched 2026-10-11; the code in it is tested by `tests/test_mcp_server.py` | passing |
| R6 | KIT.md at or under 600 lines (goal) | `./build_kit.sh` line in check.txt, after rebase on main | planned, not yet run |
| R7 | Plugin still valid (README offers plugin install) | `claude plugin validate .` in check.txt | planned, not yet run |
| R8 | No company names, interview details, personal data or secrets (public repo) | gitleaks + grep for emails, phones and company names in check.txt | planned, not yet run |
| R9 | Wiki updated (goal) | `wiki/index.md` diff in the commit | planned, not yet run |
| R10 | Structured output, retrieval, interrupt patterns, the API watchlist, practice problem, dry run | deferred: owned by session code-c7 by agreement on 2026-10-11 | deferred |

Completion records: this plan names one, the commit message plus `wiki/index.md` "In progress and next". Both carry R10 as a deferred line naming code-c7 as owner.

## Success and disproof

> **CORE-SUCCESS-DISPROOF** (blocking): The plan defines the evidence that would show success and a concrete condition that would disprove the approach. Each success measure is the property the plan claims, or a check that directly tests that property, not a stand-in for it: a count, a picture, a readability judgment, or the pipeline agreeing with itself (hashes, labels, byte equality) does not show correctness or conformance it does not test. A plan fails this item if it has no disproof condition, or if a success measure is such a stand-in for the claimed property and the plan names no direct check of that property.

> **CORE-TRACE-REVIEW** (blocking): Every success or acceptance criterion in the plan is judged from the full trace of a run, not only its final outcome: it names the run whose full trace is examined (for example the session, its tool and LLM calls, commits, check output, or messages), where that trace lives, and what must be seen in that trace beyond the final outcome. A criterion that names only an outcome, such as tests passing, a PR merged, a test fixture reproducing the journey, or a status reading succeeded, fails this item. A criterion for which no run exists, such as a pure document edit, passes only when the plan states that exemption and its reason explicitly.

**Success:** each test drives the real pattern code through scripted fake models (or the MCP SDK's in-memory client) and asserts the property the pattern exists for: the supervisor calls the right specialist tool and the specialist's own final answer comes back as that tool's result; with two specialists both answers come back in order; streaming yields the agent, tools, agent steps in order with their content; the MCP server lists the tool with its docstring and schema, returns the result, and flags a bad id as an error whose message the model can read. docs/plans/mutation.txt shows each property failing its test when the code is broken.

**Disproof:** a pattern cannot run on the installed versions as the current docs describe, a test still passes with its pattern broken, or the additions push KIT.md past 600 lines.

**Trace review:** the run judged is the check run on the final commit after rebasing on main; no live model or agent runs under this plan (scripted fakes and an in-memory MCP client only). Its full output, with commands and exit statuses, is saved as `docs/plans/kit-v2-patterns-c5.check.txt` and committed, next to `docs/plans/mutation.txt`. Beyond the final pass it must show: every test by name with PASSED and none skipped; the mutation runs' FAILED lines; the build_kit line count; plugin validate; and the privacy grep with no matches. For each success criterion the test asserts the observed values, so a PASSED line means those values were seen: for the MCP server, the listed tool's name, the docstring text in its description and the `string` type in its input schema; the returned text `Order A-100: shipped`; `is_error` true with `Unknown order id 'Z-9'` in the content. For streaming, the exact (node, text) sequence. For the supervisor, the ToolMessage names and contents. On any failure, pytest's assertion diff in check.txt shows the observed values. The supervisor tests assert the ToolMessage names and contents (the path taken), and the streaming test asserts the full step sequence, so the trace shows the route, not just the answer.

## When a run fails or surprises us

> **CORE-TRACE-DEBUGGING** (blocking): The plan includes a separate When a run fails or surprises us procedure, distinct from anticipated failure modes. It requires preserving the failed run and its trace id; reading full inputs, prompts, each tool call arguments/results, intermediate stages and final output before selecting a fix; citing the observed divergence; classifying evidence absent, evidence returned but unused or contradicted, invalid expectation, or unresolved; and linking a targeted repair to a new traced verification run while retaining the original failure. Unresolved diagnoses permit investigation but cannot authorize a causal repair. Review completeness is separate from the run verdict.

Keep the failing run: its trace id is the commit hash plus the test node id (e.g. `tests/test_mcp_server.py::test_mcp_tool_call_returns_result_and_errors_are_flagged` at the worktree's HEAD), and its full pytest output with assertion diffs goes into the session notes and read it in full before changing code: the full inputs (the user question and every scripted fake reply, which are the only prompts in an offline run), the system prompt passed to the model, each node's update, the tool call arguments and results, and the final state. Name the divergence and classify it: evidence absent (the value never came back), returned but unused or contradicted, invalid expectation (the test is wrong), or unresolved. Unresolved allows more reading (context7, installed package source) but not a fix on a guess. A fix is linked to a new traced verification run: the same test node id rerun at the fixed commit, whose output is saved next to the original failure, which stays recorded. Example from this work: the MCP error test failed because mcp 2.x hides non-ToolError messages; read in `mcp/server/mcpserver/tools/base.py`, classified as invalid expectation in the example code, fixed by raising ToolError, rerun PASSED.

## System model

> **CORE-SYSTEM-MODEL** (blocking): The plan links the project's system model (a path such as docs/model/ODD.md) or carries the one-line exemption `System model: exempt -- <reason>`, which fits only a project with no stored state and no user-facing view. Unless exempt, the plan names each system-model element (entity, process, record or event, or view) that the work adds, changes, or relies on, and its trace review names, for each such element, what the examined run must show of it (for example an event of that record type with its id, or the view displaying that entity). A plan with neither a model link nor the exemption line fails this item, as does one that lists model elements without saying what the examined run must show of each, or one that names no element without stating that the work touches none and why. For a maintained repository, the plan also cites the documentation entry point from which the model is reachable; a shared model explicitly identifies this repository's scope. It names applicable source-linked views, explains material omissions without imposing a fixed diagram quota, names concrete model freshness or drift checks, and states how the model, view coverage and verification evidence will be reconciled in the same change (or gives a concrete reason each needs no update). A bare model path without these discovery, view, freshness and reconciliation obligations fails this item. Representation Router may render selected views but does not supply planning authority or prove executed behavior.

System model: exempt -- documentation and example-code repo with no stored state, no service and no user-facing view, so no source-linked views apply

Documentation entry point: `wiki/index.md` (linked from `README.md`, "Working on this repo"); it states what the repo does and maps every file, and is where a system model would be linked if the repo ever gained state or a view. Freshness and reconciliation: there is no model to drift; the repo's map of files is `wiki/index.md` (Map table), which this change updates in the same commit with the new files, and its Evidence section records this check run. The drift check is the workspace `md_file_cap.py --repo` reachability check, which fails if a new skill page is not linked from `wiki/index.md`.

## Capability reuse

> **CORE-CAPABILITY-REUSE** (blocking): The plan answers capability reuse against the capability catalogue in agentic-capability-architecture-canonical, which has two files: `reuse_candidates.yml`, whose entries under `candidates:` are cross-project capabilities with their selected off-the-shelf implementations, each named by its `id` (for example `documents_to_text`) and marked candidate or promoted; and `capability_registry.yml`, whose entries under `capabilities:` are the packages that repository holds, each named by its key (for example `approvals`) with the capability ids it `provides` (for example `approval.resolve`). An entry from either file counts. The plan names each catalogue capability the work reuses, by its id, key or provided id; names each new capability the work adds together with its first consumer (the project, command or workflow in this plan that uses it); and, where no entry covers what the work needs, states `No catalogue entry fits, because <reason>`, the reason saying what the work needs that no entry provides. A plan may give more than one of these answers. A plan fails this item if it gives none of them, if it claims reuse without naming the catalogue entry or id reused (reusing code or a contract that is not a catalogue entry does not count), if it adds a capability without naming its first consumer, or if it says no entry fits without a reason.

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because the need is notes and example code readable by a third-party hosted IDE's assistant with no access to the workspace. The code reuses off-the-shelf libraries only (LangGraph `ToolNode`, `StructuredTool`, `graph.stream`; the official `mcp` SDK's `MCPServer` and in-memory `Client`).

## Authority and non-goals

> **CORE-AUTHORITY-NONGOALS** (blocking): The plan states who holds authority over the work and what it explicitly will not do (non-goals).

**Authority:** the owner owns the repo and set this goal in the session on 2026-10-11; he does not review PRs, so the agent merges to main and pushes after the local checks pass. The file split with the other session (code-c7) was agreed by message on 2026-10-11.

**Non-goals:** no company names, interview details or personal data; no hosted CI; no live or paid LLM calls; no edits to code-c7's files; no A2A or langchain-mcp-adapters code (both named in the note as untested).

## Irreversible actions and spend

> **CORE-IRREVERSIBLE-SPEND** (blocking): For each irreversible action or spend the plan proposes, it names the boundary, who must authorize it, and how it is contained.

One irreversible action, no spend.

- **Action and boundary:** `git push origin main` to the public GitHub repo. That is the publication boundary: before it everything is local and revertible; after it the content may be cached or copied, so a later `git revert` removes it from the repo but not from caches.
- **Who authorizes:** the owner. He authorized this class of publication in advance (workspace rule, 2026-10-07: "i dont care what is public as long as it doesnt contain private data"; 2026-10-04: "yes you can deploy anything that doesnt have private information publicly"), and set this goal, which says "push to main after checks pass". No other approval applies.
- **Containment:** the push happens only after the privacy check (R8: gitleaks plus a grep for emails, phones and company names on the whole diff) prints no matches in check.txt; the content is generic example code and notes; if anything private is found after the push, revert at once and tell the owner.

## Uncertainties

> **CORE-UNCERTAINTIES** (blocking): The plan lists its material uncertainties, and each one has an owner or the evidence that would resolve it.

| Uncertainty | Owner or resolving evidence |
|---|---|
| KIT.md line count after both sessions' additions | resolved by `./build_kit.sh` after rebasing on main; if over 600, trim my sections first |
| pyproject.toml / uv.lock merge with code-c7's langchain addition | resolved by rebase: re-run `uv add "mcp>=2.3.0"` on top of main's pyproject and commit the regenerated lock |
| Whether the IDE's chat reads these skills as intended | owner: later dry run (code-c7 item 6); not gating |

## Activation facts

> **CORE-ACTIVATION-FACTS** (blocking): No activation fact that the plan triggers is declared false. Declaring a fact true when the plan does not strictly need it is acceptable, because it only adds checks; judge only facts declared false. empirical_comparison_proposed is triggered when the plan proposes an A/B test, benchmark, bake-off, or other experiment comparing alternative designs, models, or candidates to choose among them; checking the built result against an expected outcome (an acceptance test, fixture replay, or regression check) is verification and does not trigger it. shared_mechanism is triggered by a new shared mechanism, contract, or algorithm; llm_central by behavior that centrally depends on LLM calls; irreversible_or_spend_action by a proposed irreversible action or spend. claims_external_standard is triggered when the plan claims, or presents its work as, following, implementing or conforming to a standard, schema or contract owned outside the repository being changed (for example a model presented as DM2, or output said to match a published schema); conforming to the repository's own contracts does not trigger it; aes_governed_target when the target repository is governed by an AES target (`.aes/target.yaml`). These two facts are optional: an undeclared one is shown as false and is judged like a declared false.

- empirical_comparison_proposed: false. No comparison of alternatives; tests check the built patterns against expected outcomes.
- shared_mechanism: false. The supervisor, streaming and MCP pieces are copyable examples inside this one repo, consumed by a candidate pasting them into their own project; no other project imports them, no contract between projects changes, and the algorithms are the libraries' own (LangGraph's ToolNode loop, `graph.stream`, the MCP SDK). Nothing here is a shared mechanism other projects are expected to rely on.
- llm_central: true. The supervisor's routing depends on a model choosing a specialist tool, so the pattern's behavior centrally depends on LLM calls; the call boundary and authority are under LLM calls.
- irreversible_or_spend_action: true. The public push is publication that cannot be fully undone; its boundary, authorizer and containment are under Irreversible actions and spend.
- aes_governed_target: false. The repo has no `.aes/target.yaml`; its `.aes/` folder holds only `commit_rule.yaml` (the per-repo commit rule), checked with `ls .aes/` on 2026-10-11.
- claims_external_standard: not declared (false). The note describes MCP and A2A, and the MCP example uses the official SDK, but the kit does not claim conformance to either specification.

## LLM call boundary

> **OV-LLM-CALL-BOUNDARY**, **OV-LLM-AUTHORITY-PROMOTION**

**Call graph.** Supervisor pattern: one supervisor model call per loop turn (`supervisor` node: `llm.bind_tools(specialists).invoke([SystemMessage, *messages])`); when it returns tool calls, each chosen specialist runs its own graph, which makes one model call per turn of its own loop (`agent` node of `examples/agent_template.py`) plus its tool calls; the loop ends when the supervisor replies without a tool call, bounded by `recursion_limit=10` at both levels. Streaming wraps the same calls and adds none. The MCP server makes no model call.

**Structured result boundary.** Every model call returns an `AIMessage`; its `tool_calls` list (name, args dict, id) is the structured part, validated by LangChain against each tool's argument schema before the tool runs (`ToolNode` with `handle_tool_errors=True` returns a validation failure to the model as a ToolMessage instead of crashing). A specialist returns only its final message's text, as a `ToolMessage` with the tool's name.

**Tracing.** Each node logs its tool calls (`log.info("supervisor: tool_calls=%s", ...)`, `specialist %s: %d chars`), and `stream_steps()` yields every node update in order, which is the trace a candidate prints. In this plan's runs every model is a scripted fake, so the trace is the pytest output in check.txt with the scripted replies in the test file.

**Provider and spend authority.** This plan makes no live model call and spends nothing. The examples' live path (`__main__` in `examples/agent_template.py`) uses OpenRouter (`OPENROUTER_API_KEY`, `openai/gpt-4o-mini`) or OpenAI. In a test, the candidate's own key and the test's rules are the authority; in this repo, the owner's OpenRouter route is the authority for any future live check.

**Authentic-run condition before promotion.** The kit presents these patterns as offline-tested control flow only. Before any text in the kit claims the supervisor routes correctly with a real model, one live run through OpenRouter must show, in its logged trace, the supervisor choosing `ask_orders` for an order question and the specialist's answer returning as that tool's result. Until then the skill does not make that claim.

## Vertical and reset

> **OV-PROTO-VERTICAL-RESET** (blocking): The plan names the minimal vertical result, the reset boundary, and the non-goals, without adding coordinated-work ceremony.

**Minimal vertical result:** the supervisor pattern end to end: code in `examples/patterns_multi.py`, test PASSED offline, a section in `skills/langgraph-agent/SKILL.md`, KIT.md rebuilt. Streaming, the MCP server and the note follow the same path.

**Reset boundary:** if a pattern cannot run offline on the installed versions after two attempts, drop it, record why in `wiki/index.md`, continue.

**Non-goals:** no company names, interview details or personal data; no live or paid LLM calls; no edits to code-c7's files; no A2A or langchain-mcp-adapters code.

**No coordinated-work ceremony:** no claims, no plan-owned worktree process and no handoff documents. The only coordination is one message exchange with code-c7 agreeing which files each session edits, plus a plain git worktree so the two don't share a checkout.
