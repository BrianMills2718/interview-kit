# Decisions: when to ask, when to decide, how to record it

## Decide or ask

Confidence decides. In a timed test you can rarely ask, so:

- **High confidence, or cheap to reverse**: decide, and write one ADR row in
  `docs/DECISIONS.md` (below); the README's Design decisions names the ones that matter most. Do not ask.
- **Low confidence and it changes the outcome** (the task is ambiguous about what "done" is):
  if you can ask the interviewer, ask one atomic question with your recommendation attached.
  If you cannot, pick the reading that keeps the most options open, state it as an assumption,
  and test it.

When you ask, in this order: what you understood; what you recommend; how confident you are;
what is at stake; the alternatives; the one question.

## Record it

An Architecture Decision Record (Nygard: context, decision, consequences), one row each:

| ID | Context | Decision | Consequences | Rejected alternative | What would show it wrong |
|---|---|---|---|---|---|
| ADR-1 | several specialist tasks, one conversation | specialists as tools, not a handoff swarm | one loop, testable with a fake model | langgraph-supervisor | a task needs agents to hand control mid-conversation |

"What would show it wrong" is a concrete, checkable condition (a test, a case, a number), not "revisit later".

## Prior art first

Order of preference: (1) something already does it, use it (a library function, a prebuilt
agent); (2) combine or configure existing pieces; (3) write it yourself, only for what nothing
covers, and say why in the decision row. Writing your own retry loop, parser or agent framework
in a 4-hour test is almost always the wrong call.
