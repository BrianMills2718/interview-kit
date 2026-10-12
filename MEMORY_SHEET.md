# Memory sheet: the whole method as eight short prompts

For a test that allows no outside files. Learn this page, then close it: in the test, type each
prompt from memory, in your own words. They are short on purpose. The assistant writes the
files; your job is to ask for the right things in the right order and check what comes back.
That is also what "how you use the AI" is graded on.

## The eight prompts, in order

1. **Rules.** "Work in small steps with me. No code until I approve a plan. After every change run
   the tests and show the real output. No bare except or silent fallbacks. A one-line docstring
   on every function."
2. **Plan.** "Write PLAN.md: the goal, with the task's requirements quoted as R1, R2 and so on.
   A checkable done-when list. Five to eight small steps. Assumptions and risks." Read it, fix it,
   then type "plan approved".
3. **Design.** "Write docs/DESIGN.md: outcome, the requirements as a table (R1, R2...), failure
   modes, the business rules in the order they are checked, one good and one bad test input for
   each rule, build order."
4. **Diagrams.** "Write docs/MODEL.md with six Mermaid diagrams. Give each one a question as its
   heading and a bold Answer line under it. The six are: context, the agent loop (show where it
   pauses), the main sequence, the rules as a table, the run states, and the data models.
   Then four tables: Runtime (which function writes each record), Contracts (what passes
   between parts and how it fails), Quality (each goal and the test that proves it), Unknowns.
   Use only real function names."
5. **Decisions.** "Write docs/DECISIONS.md as a table with rows D1, D2...: each choice, why, the
   alternative I rejected, and what would prove it wrong."
6. **Build, one slice at a time.** "Implement step N only, with a test a wrong version would fail.
   Use a fake scripted model so the tests run offline. Run the tests." Repeat for each step.
7. **Check against the plan.** "Act as a reviewer. Check the code against PLAN.md and the
   diagrams. List anything missing, untested, or drawn but not in the code." Fix what it finds.
8. **README.** "Write README.md: how to run it, the approach (include the agent-loop and rules
   diagrams), design decisions, assumptions, how I used the AI (where it was wrong and what I
   changed), limitations and next steps."

## Four hours
0:00 read the task twice, prompts 1-2 · 0:30 prompts 3-5 · 1:00 prompt 6 until done ·
2:45 prompt 7, failure cases · 3:15 prompt 8 · 3:30 run everything once more, submit.

## Check these yourself (the assistant gets them wrong)
- `create_react_agent` is old: use `from langchain.agents import create_agent` and `system_prompt=`.
- Structured answer: `response_format=ToolStrategy(Model)`, read from `out["structured_response"]`.
- Bound the loop: `recursion_limit` set to something small, like 10.
- Human pause: `interrupt()` returns to the caller, and you resume with `Command(resume=...)` on
  the same `thread_id`. **The tool runs again from its first line**, so do the write (the refund)
  only after `interrupt()` returns.
- Mermaid breaks on `;` in a sequence message and on parentheses in a class field.
  Quote labels that have parentheses: `A["get_order()"]`.

## What to keep a note of while you work
Every time the assistant was wrong and you corrected it. Those notes go in the README's AI section,
and they are the strongest evidence of good AI use.
