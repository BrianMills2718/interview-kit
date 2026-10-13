# Memory sheet: what to type, in order

The words to type into the IDE's AI chat, close to verbatim. Learn the fourteen **bold names** in
order first; the wording under each follows from its name. `<...>` is what you fill in from the
task. **[Ask]**, **[Plan]** and **[Edit]** are the chat's modes: Ask and Plan change nothing,
Edit writes files. The order is the Unified Process: agree the intent, write the use cases
(failures too), draw the things and their states, find what already exists, choose the shape,
draw the riskiest case, plan, then build in small checked steps with one test per arrow. Draw a
diagram only when it answers a question. At the three decision points (intent, riskiest case,
shape) you say what you think first and the AI argues with it. If a recorded test grades how you
use the AI, this is also what it sees.

## Before the first prompt

Switch the chat to the strongest model offered. If outside files are allowed, run
`git clone <kit url> kit` in the terminal, send prompt 1 as written, and add one line: "Also read
kit/AGENTS.md and follow it all session."

## The fourteen prompts

**1. Rules** [Ask]
> We work in small steps. No solution code until I type "plan approved"; small check scripts
> are fine. After every change, run the
> tests and show me the real output. No bare except, no silent fallbacks. A one-line docstring on
> every function. When you are unsure, say so instead of guessing.

**2. Intent** [Ask]
> Read the task. Don't solve anything yet. My reading: <who uses it, what they get, what done
> looks like>. Critique my reading: what did I miss or get wrong? Then list every requirement as
> R1, R2..., quoting the task's exact words. Then list what is ambiguous or missing.

**3. Questions** [Ask]
> Ask me your questions one at a time, most important first, at most seven. Give your recommended answer with
> each so I can just say yes or correct it.

Answer each one. Then:
> Write my answers down as assumptions A1, A2..., each with the requirement it affects.

**4. Use cases and risks** [Ask]
> List the use cases: the normal path first, then every failure and alternative (bad input,
> a "no", a retry, a limit). Then rank the risks, riskiest first, each with how we test it early.
> I think the riskiest is <use case>, because <reason>. Do you agree? Argue if not.

Then [Edit]:
> Write docs/PRD.md with these headings: ## Goal, one line (who, what, why this shape) and an
> "Example: <input> -> <result>" line; ## Requirements, a table | ID | Quoted from the task |
> Reading chosen, if ambiguous | with rows | R1 |; ## Use cases, a table | ID | Kind | Actor |
> Trigger | Steps | Expected result | with rows | UC1 |, where Kind is normal, failure or
> alternative; ## Assumptions, a table | ID | Assumption | Requirement it affects | with rows
> | A1 |; ## Risks, a table | ID | Risk | Use case | How we test it early | with rows | K1 |,
> riskiest first.

**5. Domain model and states** [Edit]
> Start docs/MODEL.md. Under ## Domain model: a Mermaid classDiagram of the things in the use
> cases and the typed records, a bold **Answer:** line, and a "Rules:" list of what must always be
> true. Under ## State machine: a Mermaid stateDiagram-v2 of the run, with the human pause and
> the resume, a bold **Answer:** line, and a "Forbidden:" list of transitions that must never
> happen, written "A --> B". If nothing has states, write one line: "No states: <reason>".

Then question the drawing:
> Walk me through the state machine when <the riskiest use case> happens. Which arrow fires,
> and what stops a forbidden one?

(`bash kit/check.sh` fails PLAN.md, docs/DECISIONS.md, "## Sequence" and "## Tests from the model"
until prompts 8-10; that is expected.)

**6. Off the shelf** [Ask]
> For each requirement, what already does it? Name the library, the exact import and function,
> and the version installed here. Prefer what is already installed, then the standard library,
> then a well-known package. Mark anything we have to build ourselves and say why nothing
> existing fits.

**7. Prove it** [Edit]
> Write check_imports.py that imports every function you just named and prints each package's
> installed version. Run it and show me the output.

Then:
> Which of those were wrong or out of date? Fix the list.

Then:
> Write a probe script of about ten lines that tries the library behaviour the riskiest use case
> depends on (for a human pause: pause, resume once, print which lines ran twice). Run it and show
> me the output.

**8. Shape** [Ask]
> I want to shape it as <one agent with tools, a fixed graph, a router, or plain code>, because
> <reason>. Argue against it: what breaks, and what would you pick instead?

Then [Edit]:
> Write docs/DECISIONS.md as ADRs: a table | ID | Context | Decision | Consequences | Rejected
> alternative | What would show it wrong |, one row per choice so far (the shape and each
> library), rows | ADR-1 |, | ADR-2 |...

**9. Riskiest case and tests** [Edit]
> In docs/MODEL.md add ## Sequence: <UC id> <name> for the riskiest use case: a Mermaid
> sequenceDiagram with a bold **Answer:** line. Use the real library functions from prompt 7 and
> name our functions exactly as we will write them. Then add ## Tests from the model, a table
> | Claim | From | Test |: one row per arrow in the state machine, copied as written "A --> B",
> including [*]; one row per Forbidden line; one row per domain rule; one row per requirement whose
> exact output the task quotes, From = its R id. Name each test `test_...`.
> In backticks with (), name only functions our code defines or imports, never a method such as
> `graph.invoke()`: `check.sh --final` fails names the code does not define.

**10. Plan** [Plan]
> Write a plan with these headings: ## Goal, with the requirements R1, R2...; ## Done when, a
> checklist; ## Steps, five to eight small steps, each naming the `test_...` rows from
> docs/MODEL.md it makes pass, step 1 the thinnest end-to-end slice through the
> entry function for the riskiest use case, its test first; ## Shape, the shape chosen and one
> line per rejected shape; ## System model, a link to docs/MODEL.md; ## Assumptions; ## Risks.

Read it, correct it, then [Edit]: "Save that plan as PLAN.md." Then type: "plan approved".

**11. Build one step** [Edit]. Repeat for each step.
> Implement step <N> only. Write the tests PLAN.md names for it, each one a wrong version
> would fail, and where the model is involved, use a fake scripted model so it runs offline. Use
> the function names in docs/MODEL.md.
> Also test what the diagrams forbid: every Forbidden line in docs/MODEL.md, and that nothing is
> written on a "no". Never change a diagram or a test just to make the code pass: if the model is wrong, tell me
> why and update the diagram and its test together. Run the tests and show me the output.

Then:
> Explain in two sentences what you just wrote.

**12. Review** [Ask]
> Act as a reviewer. Check the code against PLAN.md, docs/PRD.md and docs/MODEL.md. List any use
> case, arrow or rule with no test, anything drawn but not in the code, and anything in the code
> but not drawn.

Fix what it finds, one finding at a time, with prompt 11, saying "Fix finding <n> only" in place
of "Implement step <N> only".

**13. README** [Edit]
> Write README.md with these ## headings in order: ## Run it (the one command that runs it end to
> end, such as the task's grader or demo, and its real output),
> ## Approach (include the state machine and the sequence diagram), ## Off-the-shelf parts,
> ## Design decisions (link docs/DECISIONS.md), ## Assumptions, ## How I used the AI (where it
> was wrong and what I changed), ## Limitations, ## Next steps.

**14. Finish** [Edit]
> Run every test, the README's Run it command and `bash kit/check.sh --final`.
> Tick each Done when item in PLAN.md and write the real result next to it (the actual pass count, not a placeholder).
> Run `bash kit/check.sh --final` again, put its last line on the check.sh item, and show me
> anything still unticked.

## When it is wrong (any time)
> That's wrong: <what>. Fix it, and add a line to the README's AI notes saying what you got wrong
> and how we caught it.

## Four hours
0:00 read the task twice, prompts 1-3 · 0:25 prompt 4 · 0:45 prompt 5 · 1:00 prompts 6-8 ·
1:20 prompts 9-10 · 1:35 prompt 11 until done · 2:50 prompt 12, failure cases · 3:15 prompt 13 ·
3:25 prompt 14 · 3:40 submit.

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
