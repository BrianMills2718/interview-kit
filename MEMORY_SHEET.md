# Memory sheet: what to type, in order

The words to type into the IDE's AI chat, close to verbatim. Learn the thirteen **bold names** in
order first; the wording under each follows from its name. `<...>` is what you fill in from the
task. **[Ask]**, **[Plan]** and **[Edit]** are the chat's modes: Ask and Plan change nothing,
Edit writes files. The order is the method: agree the intent, find what already exists, draw it,
plan, then build in small checked steps. If a recorded test grades how you use the AI, this is
also what it sees.

## Before the first prompt

Switch the chat to the strongest model offered. If outside files are allowed, run
`git clone <kit url> kit` in the terminal and replace prompt 1 with: "Read kit/AGENTS.md and
follow it all session."

## The thirteen prompts

**1. Rules** [Ask]
> We work in small steps. No solution code until I type "plan approved"; small check scripts
> are fine. After every change, run the
> tests and show me the real output. No bare except, no silent fallbacks. A one-line docstring on
> every function. When you are unsure, say so instead of guessing.

**2. Intent** [Ask]
> Read the task. Don't solve anything yet. Tell me in your own words: who uses this, what they
> get, and what done looks like. Then list every requirement as R1, R2..., quoting the task's
> exact words. Then list what is ambiguous or missing.

**3. Questions** [Ask]
> Ask me your questions one at a time, most important first. Give your recommended answer with
> each so I can just say yes or correct it.

Answer each one. Then:
> Write my answers down as assumptions A1, A2..., each with the requirement it affects.

**4. Off the shelf** [Ask]
> For each requirement, what already does it? Name the library, the exact import and function,
> and the version installed here. Prefer what is already installed, then the standard library,
> then a well-known package. Mark anything we have to build ourselves and say why nothing
> existing fits.

**5. Prove it** [Edit]
> Write check_imports.py that imports every function you just named and prints each package's
> installed version. Run it and show me the output.

Then:
> Which of those were wrong or out of date? Fix the list.

**6. Options** [Ask]
> Give me two or three ways to shape this, for example one agent with tools, a fixed graph, or
> a router. For each: what it is good at, what breaks, and which you would pick here and why.

Then choose:
> Go with <option>, because <reason>.

**7. Diagrams** [Edit]
> Before any code, write docs/MODEL.md with six Mermaid diagrams, headed "## 1." to "## 6." with a
> question each and a bold Answer line under each: 1 context (flowchart), 2 the agent loop, showing
> where it pauses (flowchart), 3 the main sequence (sequenceDiagram), 4 the rules as a table plus a
> flowchart, 5 the run states (stateDiagram-v2), 6 the data models (classDiagram). Then four
> tables: Runtime (which function writes each record), Contracts (what passes between parts and
> how it fails), Quality (each goal and the test that proves it), Unknowns. Use the real library
> functions from prompt 5, and name our own functions exactly as we will write them.

Then question the drawing:
> Walk me through the agent-loop diagram when <the hardest case in the task> happens. What does
> each part do?

**8. Design and decisions** [Edit]
> Write docs/DESIGN.md with these sections: Outcome; Requirements, a table with rows R1, R2...;
> Failure modes; Domain rules, in the order they are checked; Fixtures, one good and one bad input
> per rule; Slices, the build order. Then write docs/DECISIONS.md as a table with rows D1, D2...: each choice
> we made, why, the alternative we rejected, and what would prove it wrong.

**9. Plan** [Plan]
> Write PLAN.md with these headings: ## Goal, with the requirements R1, R2...; ## Done when, a
> checklist; ## Steps, five to eight small steps in the build order; ## System model, the shape we
> chose and a link to docs/MODEL.md; ## Assumptions and risks.

Read it, correct it, then type: "plan approved".

**10. Build one step** [Edit]. Repeat for each step.
> Implement step <N> only. Write a test a wrong version would fail, and where the model is
> involved, use a fake scripted model so it runs offline. Use the function names in docs/MODEL.md. Run the tests and show me the output.

Then:
> Explain in two sentences what you just wrote.

**11. Review** [Ask]
> Act as a reviewer. Check the code against PLAN.md, the requirements and the diagrams. List
> anything missing, untested, or drawn but not in the code.

Fix what it finds, one step at a time, with prompt 10.

**12. README** [Edit]
> Write README.md with a "## Run it" section first (the exact command and its output), then: the approach (include the agent-loop and rules diagrams), the
> off-the-shelf parts we used and why, design decisions, assumptions, how I used the AI (where it
> was wrong and what I changed), limitations, and next steps.

**13. Finish** [Edit]
> Run every test and the main command once more. Tick each Done when item in PLAN.md and write the
> real result next to it (the actual pass count, not a placeholder). Then show me anything that
> is still unticked.

## When it is wrong (any time)
> That's wrong: <what>. Fix it, and add a line to the README's AI notes saying what you got wrong
> and how we caught it.

## Four hours
0:00 read the task twice, prompts 1-3 · 0:30 prompts 4-6 · 1:00 prompts 7-9 ·
1:30 prompt 10 until done · 2:45 prompt 11, failure cases · 3:15 prompt 12 · 3:25 prompt 13 ·
3:40 submit.

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
