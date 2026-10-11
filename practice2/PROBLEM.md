# Practice problem 2: security-alert triage agent, hidden tests (2 hours)

A second timed rehearsal, closer to a real take-home: most grading cases are hidden. You see three
worked examples; ten more cases check rules this page states but does not demonstrate.
Target 2 hours, hard stop at 4.

## How to run the practice

1. In a project folder of your own, `git init` if needed, then `git clone <this kit> kit` inside it.
2. Remove both practice answers before reading anything else (the first problem's answer shows this one's patterns):
   `python3 -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ('kit/practice/reference', 'kit/practice2/reference')]"`.
   Install: `uv venv && uv pip install langchain langgraph pytest` (`check.sh` uses `.venv`).
   Do not decode `kit/practice2/hidden.b64`; it is not secret, only out of sight, like a real hidden suite.
3. Start a timer. Use only the kit's files and one AI chat, as the IDE would allow.
4. Done = `.venv/bin/python kit/practice2/grade.py solution.py` exits 0 and `bash kit/check.sh --final` exits 0.
   A failing hidden case shows only its name and which check failed; find the rule here, write
   your own test for it, then fix.
5. Write down the elapsed time, every place you got stuck, and which hidden cases failed first.

## The task

Build a security triage agent with LangGraph or LangChain in `solution.py`. Data is in
`kit/practice2/data.json` (hosts, known-bad IPs, logs).

| Tool | Does | Returns exactly |
|---|---|---|
| `get_host(name)` | look up a host; name case does not matter | `web-1: prod, owner storefront, ip 10.0.0.5` (name in lower case), or `Host X not found.` (X as given) |
| `search_logs(host, term)` | that host's log lines whose text contains term; host and term ignore case; newest first, at most 3 | one line each, `L-3 2026-03-01T10:02 <text>`, joined by newlines; `No matching logs.`; `Host X not found.` |
| `block_ip(ip, reason)` | block an address | see rules below |

`search_logs` may run at most 4 times per agent built by `build_agent` (every call counts, unknown hosts included); after that every call returns `Search limit reached (4).`

Block rules, checked in this order:

1. Not an IPv4 address: `Invalid IP: X.`
2. Inside 10.0.0.0/8: `Refused: X is internal.`
3. Already blocked: `X is already blocked.`
4. Listed in `known_bad`: block it with no pause, `Blocked X (known bad).`
5. Otherwise pause and ask a human reviewer first. On `yes` (any case, spaces ignored): `Blocked X after approval.` Otherwise: `Block of X declined by reviewer.`

A block is recorded by appending the IP to `soc["blocked"]`. Several blocks asked for in one model turn
may pause together; the grader gives every pending pause the same answer.

The final answer is a validated `Verdict`: `severity` (low, medium, high or critical), `host`
(a host name written in lower case, otherwise invalid; or none), `action` (one sentence), `evidence` (log ids like `L-3`).
High or critical needs at least one evidence id. An invalid verdict goes back to the model to retry.

## Interface the grader uses

```python
def build_agent(llm, soc):   # soc = data.json as a dict, plus soc["blocked"] = []
    ...                      # return a compiled graph with a checkpointer
```

The grader calls `graph.invoke({"messages": [HumanMessage(text)]}, config)`, and while the result
has `__interrupt__` it resumes with `Command(resume="yes" or "no")`. It reads
`result["structured_response"]`. The model is scripted (no API key): it calls your tools by name,
sometimes several in one turn, and gives the final answer by calling a tool named `Verdict`.

## Graded on

All grader cases pass, hidden ones included; your own tests, one per rule above; the planning
package in `docs/` (DESIGN, MODEL with six diagrams, DECISIONS, from `kit/templates/`); a README
with Run it, Approach, Design decisions, AI use and Limitations; a clear, honest account of how
you used the AI chat.
