# Diagrams and pages a person reads

Before drawing, write the question the reader has ("which part writes the refund?") and what
they will do with the answer. Then pick the form.

- **Title says what it is and for whom.** "Refund flow: what happens to a $70 refund request",
  not "Diagram 1".
- **The whole thing is readable in a minute.** If it is not, split it, or cut detail.
- **Form matches job**: a sequence for order, a table for comparison, a state diagram for
  status, a list for a straight chain.
- **Draw relationships; do not imply them** with position or colour alone.
- **One visual language per page**: the same shape means the same thing everywhere.
- **Nothing invented**: every element is real (see architecture-views.md); unknowns are marked
  "unknown", not drawn as if known.
- **Colour is never the only signal**: add a word or a dashed line, and avoid red against green.
- **Show the mechanism the decision rests on**: if the design depends on how a library behaves
  (a pause returns to the caller; a resume re-runs the tool), draw that behaviour exactly.
- **A table, not a flowchart, for a straight chain of checks**; draw only the branching part.

For a take-home: the six diagrams live in `docs/MODEL.md`, each under a heading that is its
question with a bold "Answer:" line beneath it. The README shows the two a reviewer needs first,
the agent loop (diagram 2) and the rules (diagram 4), and links to the rest. Before finishing,
check each diagram against the code: every node, arrow and row is something the code does.

**Check every diagram renders** before you finish: paste each block into mermaid.live, or run
`npx --yes @mermaid-js/mermaid-cli -i docs/MODEL.md -o .render/MODEL.md`. If it cannot find
Chrome, point it at an installed one with `-p puppeteer.json` containing
`{"executablePath": "<path to chrome>"}`. Quote labels that contain parentheses: `A["get_order()"]`. mermaid-cli exits 0 even when a
block fails to parse, so count its ✅ lines (one per block) rather than trusting the exit code.
Known breakers: `;` inside a sequence message or Note, parentheses in a class-diagram field
(it moves to the methods box), and `__name__` in a Note (renders as bold).
