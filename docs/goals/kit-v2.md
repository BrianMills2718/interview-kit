# Goal: kit v2, ready for a timed agentic-AI take-home

Profile: continuous-light (one writer, reversible, public repo).

**Mission.** In a hosted Python IDE (terminal, internet, pip, git) whose only allowed AI is the
IDE's own recorded chat (Ask / Plan / Edit), a candidate clones this repo, follows `AGENTS.md`,
and in 2-3 hours delivers a tested LangGraph agent for an unseen problem, with a plan, visible
verified AI use and a clear explanation.

**Canonical example.** The practice problem added below, solved from a fresh clone with only the
kit's files inside a 4-hour clock, passes `./check.sh --final`.

**In scope, one commit each, in order:**
1. `skills/using-ide-ai-chat`: Ask vs Plan vs Edit; choose the strongest model offered, not the
   default; prompts that show judgment (intent, plan, verify, note where the AI was wrong);
   clone rather than paste (pastes show in playback); avoid AI showcase, feature marathon and
   hands-off patterns.
2. Deprecated-API watchlist in `skills/langgraph-agent` (`create_react_agent` ->
   `langchain.agents.create_agent`, `prompt=` -> `system_prompt=`, supervisor/swarm add-ons ->
   subagents as tools, `langchain.chains`, `hub`, recursion limit default, fake models lacking
   `bind_tools`, `interrupt()` + `Command(resume=)`), each checked against the installed version.
3. Offline-tested patterns: Pydantic structured output, a retrieval tool, a human-in-the-loop
   interrupt, each with a fake-model test that could fail.
4. A short sourced note on MCP (SDK v2) and A2A.
5. A 2-hour practice problem in `practice/` with known-answer cases; its solution kept out of `KIT.md`.
6. Dry run of item 5 from a fresh clone, timed; fold every friction back into the kit.

**Out of scope:** company names, interview details, personal data; hosted CI; other repos.

**Done when** each of these is shown from the run's output, not a summary:
- `uv run pytest -v` lists the new tests PASSED, and one is shown failing when its behavior is broken;
- each watchlist entry names the package version it was checked against;
- `./build_kit.sh` regenerates `KIT.md`, still under about 30 KB;
- gitleaks plus an email/phone grep find nothing, and a light LLM read of changed files lists no
  company, interview or personal detail;
- the dry run's tool calls and test output are read: `./check.sh --final` exits 0, elapsed time
  is recorded, and each friction is fixed or listed in `wiki/index.md`.

**Stops.** Three attempts on one reproduced blocker with no new evidence: record it in
`wiki/index.md` with the resume event and stop. At most 8 increments; revalidate against the
mission after 3 increments or about 4 hours.

**Non-gating:** the candidate's own timed practice run; checking the IDE chat itself (needs an account).
