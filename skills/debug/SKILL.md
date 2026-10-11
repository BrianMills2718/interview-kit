---
name: debug
description: Find the root cause of a failing test, error or wrong agent answer before changing code - read, reproduce, one hypothesis at a time, fix with a test. Use whenever something fails or surprises you.
---

# Skill: debug by root cause, not by guessing

Adapted from obra/superpowers `systematic-debugging` (MIT). In a recorded test, a run of
"try this... try that..." prompts reads as lost control; a stated hypothesis tested in one small
step reads as skill.

**Rule: no fix before you can say what the cause is and why.**

## 1. Read and reproduce

- Read the whole error and stack trace: file, line, exception type, message.
- Reproduce it with one command (`pytest tests/test_x.py::test_y -v`). If it does not fail on
  demand, you are not debugging yet.
- For an agent that answers wrongly, print the trace before touching code: every message, each
  tool call with its arguments, each tool result, the final answer
  (`for step in graph.stream(..., stream_mode="updates"): print(step)`). Then decide which it is:
  - the needed fact never came back from any tool (tool or retrieval problem),
  - it came back but the model ignored or contradicted it (prompt or tool-description problem),
  - the expected answer is itself wrong (test problem).

## 2. Compare with something that works

Find the closest working example (the kit's `examples/`, the library docs, an earlier passing
commit) and list every difference, including the installed version
(`importlib.metadata.version("langgraph")`).

## 3. One hypothesis, one change

- Write it down: "I think X causes this because Y." Ask the AI chat in **Ask** mode to check
  the reasoning, not to fix it.
- Make the smallest change that tests it. Run. If it is wrong, undo it and form a new hypothesis;
  do not pile fixes on top of each other.
- Say "I don't understand X yet" when that is true, then read the source or docs.

## 4. Fix with a test

- First a test that fails for this bug, then the fix, then the full suite.
- After three failed fixes, stop and question the design rather than trying a fourth.

## Stop signs

"Quick fix for now", "just try changing X", several changes before one test run, "it's probably
X" with no evidence, or each fix revealing a new problem elsewhere. Go back to step 1.

Note the bug and its cause in the README's AI section if the AI introduced it.
