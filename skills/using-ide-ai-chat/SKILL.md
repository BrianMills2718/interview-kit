---
name: using-ide-ai-chat
description: Drive a hosted IDE's built-in AI chat (Ask / Plan / Edit modes) well and visibly when every prompt is recorded and graded. Use at the start of a timed test and before each prompt.
---

# Skill: use the IDE's AI chat so the recording shows judgment

In a recorded test the reviewer replays every prompt. They grade *how* the AI was used, not
whether it was. Source for the modes: the IDE's AI Assist docs
(coderpad.io/resources/docs/interview/pads/interview-ai-assist/).

## Setup (first 5 minutes)

1. **Pick the strongest model offered.** The default is often a small model (e.g. GPT-4o mini).
   Switch to the strongest listed (a Claude Sonnet or GPT-5 class model) before the first prompt.
2. **Bring the kit in with `git clone`, not paste.** Playback flags large pastes and "copied all
   code" events. Cloning is visible as a terminal command and reads as setup, not as pasted answers.
3. **Give the chat the rules once:** "Read kit/AGENTS.md and follow it for this session. Start
   by writing PLAN.md; do not write code yet."

## Which mode, when

| Mode | Does | Use for |
|---|---|---|
| Ask | answers, reads code, changes nothing | understanding the task, API questions, "why did this fail?" |
| Plan | proposes steps, changes nothing | the plan, and before any multi-file change |
| Edit | writes code into files | one small step at a time, after the plan exists |

Never start in Edit. Ask -> Plan -> Edit, one step per Edit prompt.

## Prompt patterns that grade well

- **State intent and constraint:** "Add a `lookup_order` tool. Raise ValueError on unknown ids.
  Do not change the graph wiring." Not "build the agent".
- **Ask for the test first:** "Write a test that fails if the tool result never reaches the
  model, then the code."
- **Make it verify:** "Run `pytest -v` and show me the output" after every Edit.
- **Check its API knowledge:** "Which langchain/langgraph version is installed? Is that function
  current in that version?" Then check with `importlib.metadata.version(...)` and the watchlist in
  `skills/langgraph-agent`. Assistants often suggest deprecated calls.
- **Correct it in the open:** when it is wrong, say what was wrong and why in the chat, and note
  it in the README's AI section. Visible corrections are evidence of judgment.
- **Ask for a critique:** "Act as the reviewer in kit/agents/reviewer.md and list problems."

## The three patterns reviewers mark down

- **AI showcase:** many clever prompts, little working code or explanation.
- **Feature marathon:** adding features past the spec instead of finishing, testing and explaining.
- **Hands-off:** accepting large generated blocks unread; unable to explain the code afterwards.

Antidote to all three: small steps, run after each, and be able to say in one sentence what each
function does.

## Last 20 minutes

Stop adding features. Run `bash kit/check.sh --final`, fill the README (see
`skills/explain-your-work`), list where the AI was wrong, and commit.
