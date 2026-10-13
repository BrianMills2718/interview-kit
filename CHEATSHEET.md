# Cheat sheet: short prompts, by stage

Keep this open beside the AI chat and type the line, filling the `___`. The full wording and the
reasons are in [MEMORY_SHEET.md](MEMORY_SHEET.md). Models are picked by the question they answer
(what, how, where, who, when, why); draw one only if its question matters for this task.

## 1. Set up
- `Rules: small steps. No code until I type "plan approved". After every change run the tests and show the output. No bare except. Say when unsure.`

## 2. Understand
- `Read the task. My reading: ___. Critique it. List requirements R1.. quoting the task. List what is ambiguous.`
- `Ask me your questions one at a time, with your recommended answer. Record my answers as assumptions A1..`

## 3. Look at the data first
- `Load the data with pandas. Show shape, column types, nulls, 5 rows, value counts of key columns, date range. No analysis yet.`
- `For each analysis the task asks for, name the method (z-score, Welch t-test, groupby, networkx degree), its assumption, and the exact threshold the task states.`

## 4. Why: requirements (PRD)
- `Write docs/PRD.md: Goal with one example; Requirements R1..; Use cases UC1.. (normal, failure, alternative) with actor, trigger, steps, result; Assumptions A1..; Risks ranked. I think the riskiest is ___.`

## 5. Model (docs/MODEL.md, Mermaid)
| Question | Model | Prompt |
|---|---|---|
| Who uses it, and what is outside it? | Context diagram | `Draw a flowchart of the system as one box, with the people, data files, LLM and other systems around it, and what flows between them.` |
| What are the things? | Domain model | `classDiagram of the things in the use cases and their fields, plus a Rules list of what must always be true.` |
| What is in the data? | Data dictionary | `Table of every input column: type, unit, allowed values, nulls, and the rule we enforce. Then the output records the same way.` |
| How does the analysis flow? | Pipeline (activity) | `flowchart of the analysis: load, validate, clean, features, detect, human review, report. Mark where bad rows go.` |
| When can things happen? | State machine | `stateDiagram-v2 of one run, with the human pause and resume, plus a Forbidden list written "A --> B".` |
| How does the riskiest case run? | Sequence | `sequenceDiagram of UC___ between user, agent, each tool, the LLM and the human, using the real library calls.` |
| Where does code live? | Components | `flowchart of the files and functions we will write and what each calls.` |
| What does each operation promise? | Contracts | `For each tool: inputs, preconditions, what it changes, what it returns, and the error it raises.` |
| How do we know it is right? | Evaluation | `Define the metric (precision, recall, F1, confusion matrix), the labelled cases, and the baseline we compare against.` |

Then: `Walk UC___ through the state diagram and the pipeline. Which arrow fires, and what stops a forbidden one?`

## 6. Off the shelf
- `For each requirement, which installed library does it? Exact import and version. Write check_imports.py and run it.`
- `Write a ten-line probe of the library behaviour the riskiest case depends on. Run it.`

## 7. Decide (docs/DECISIONS.md)
- `I'd build it as ___ because ___. Argue against it. Then write ADRs: context, decision, consequences, rejected alternative, what would show it wrong.`

## 8. Tests from the model
- `Add a table Claim | From | Test: one test per state arrow, forbidden move, domain rule, contract error, data rule, and exact output the task quotes.`

## 9. Plan
- `Write PLAN.md: Goal; Done when (checkboxes); Steps, each naming its tests, riskiest case first as a thin end-to-end slice; Shape; Assumptions; Risks.` Then type `plan approved`.

## 10. Build (repeat per step)
- `Implement step N only. Tests first, with a fake model so they run offline. Run them and show the output. Then explain it in two sentences.`

## 11. Evaluate
- `Write evaluate.py: precision, recall, F1 and a confusion matrix against the labels, beside the baseline. One paragraph on what the errors show.`

## 12. Finish
- `Review against PRD, MODEL and PLAN: any use case, arrow, rule or contract with no test, and any code not in the diagrams.`
- `README: Run it, Approach (with the diagrams), Decisions, Assumptions, How I used the AI, Limitations, Next steps. Tick Done when with real results.`

Any time: `That's wrong: ___. Fix it, and note it in the README's AI section.`
