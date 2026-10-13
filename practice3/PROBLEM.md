# Practice problem 3: social-post analysis agent, with an evaluation (3 hours)

The third timed rehearsal, for the data-analysis side of a data-science agentic take-home: an agent
whose tools do anomaly detection, coordinated-behaviour detection, a statistical test and a small
network count over posts in three languages, plus an evaluation of an LLM topic classifier. As in
practice 2, most grading cases are hidden: you see three worked examples; twelve more check rules
this page states but does not demonstrate. Target 3 hours, hard stop at 4.

## How to run the practice

1. In a project folder of your own, `git init` if needed, then `git clone <this kit> kit` inside it.
2. Remove the practice answers before reading anything else (the earlier answers show this one's patterns):
   `python3 -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ('kit/practice/reference', 'kit/practice2/reference', 'kit/practice3/reference')]"`.
   Install: `uv venv && uv pip install langchain langgraph pytest scipy` (`check.sh` uses `.venv`).
   Do not decode `kit/practice3/hidden.b64` or read `kit/practice3/make_data.py`; the first is out of
   sight like a real hidden suite, the second says where the signals were planted.
3. Start a timer. Use only the kit's files and one AI chat, as the IDE would allow.
4. Done = `.venv/bin/python kit/practice3/grade.py solution.py evaluate.py` exits 0 and `bash kit/check.sh --final` exits 0.
   A failing hidden case shows only its name and which check failed; find the rule here, write
   your own test for it, then fix.
5. Write down the elapsed time, every place you got stuck, and which hidden cases failed first.

## The data

`kit/practice3/posts.csv` (synthetic, 398 rows): `post_id` (`P0001`...), `date` (`YYYY-MM-DD HH:MM`,
minute precision, March 2026), `account_id` (`A01`...`A40`), `language` (`en`, `es` or `ru`), `text`,
`shares` (a whole number), `reply_to` (the `post_id` this post replies to, or empty).
`kit/practice3/labels.csv` (60 rows): `post_id` and its gold `topic`, one of `transport`, `weather`,
`sports`, `prices`.

## Part 1: the agent

Build it with LangGraph or LangChain in `solution.py`. Tools, with these exact names:

| Tool | Does | Returns exactly |
|---|---|---|
| `count_posts(language, start, end)` | count posts; each argument may be an empty string, meaning no filter; language ignores case; `start` and `end` are `YYYY-MM-DD`, inclusive | `37 posts: en 20, es 10, ru 7` (only languages with at least one post, in the order en, es, ru); `0 posts.`; `Unknown language: X.`; `Invalid date: X.` (X as given) |
| `daily_volume_anomalies(z)` | z-score of each day's post count; days run from the first post's day to the last post's day and a day with no posts counts as 0; mean and **population** standard deviation of those counts; a day is anomalous when its z-score, rounded to 2 decimals, is at or above `z` | one line per anomalous day, oldest first, `2026-03-04: 30 posts, z 2.41`, joined by newlines; `No anomalous days.` (also when the standard deviation is 0) |
| `find_coordinated(window_minutes, min_accounts)` | see "Coordinated groups" below | one line per group, `accounts A01,A07; posts P0003,P0005; 2026-03-02 10:00 to 2026-03-02 10:03`, joined by newlines; `No coordinated groups.` |
| `compare_shares(lang_a, lang_b)` | Welch's t-test (unequal variances) on the shares of the two languages' posts, with `scipy.stats.ttest_ind(a, b, equal_var=False)`; languages ignore case | `es vs en: mean 10.67 vs 6.86, n 118 vs 213, t 3.40, p 0.0008` (languages lower-cased, in the order given; means and t to 2 decimals, p to 4); `Unknown language: X.`; `Pick two different languages.`; `Not enough posts.` (fewer than 2 in either) |
| `top_reply_hubs(k)` | for each account, the number of replies its posts received from **other** accounts (a reply to one's own post does not count); most first, ties by account id ascending; only accounts with at least one | at most k lines `A03 14 replies`, joined by newlines; `No replies.`; `k must be at least 1.` |
| `flag_coordinated(account_ids, reason)` | record a group as coordinated, after an analyst approves | see "Flag rules" below |

**Coordinated groups.** Normalise each text: lower-case it, and replace every run of whitespace with
one space, trimming both ends. For each normalised text, take its posts in time order (ties by
`post_id`). Start with the earliest as the anchor; the window is every post of that text at most
`window_minutes` after the anchor (inclusive). If the window's posts come from at least
`min_accounts` distinct accounts, they are a group, and the next anchor is the first post after the
group; otherwise the next anchor is the next post. In a line, accounts are sorted, posts are in time
order, and the two times are the first and last post of the group. Groups are listed by their first
post's time.

**Flag rules**, checked in this order:

1. Fewer than 2 distinct accounts: `A group needs at least 2 accounts.`
2. An account that has no post (the first such, in the order given): `Account X not found.`
3. The same set of accounts already flagged (order does not matter): `Group already flagged.`
4. Otherwise pause and ask the analyst. On `yes` (any case, spaces ignored): `Flagged N accounts after approval.`
   Otherwise: `Flag declined by analyst.`

A flag is recorded by appending the sorted list of distinct account ids to `data["flagged"]`, only
after a yes. A "no" records nothing.

The final answer is a validated `Finding`: `question_type` (`count`, `volume`, `coordination`,
`shares` or `network`), `answer` (one sentence: one line ending with a full stop), `numbers` (a dict
of name to number, the figures the answer rests on), `evidence_post_ids` (ids like `P0042`). A
`coordination` finding needs at least one evidence id. An invalid Finding goes back to the model to retry.

### Interface the grader uses

```python
def build_agent(llm, data):  # data = {"posts": rows of posts.csv as csv.DictReader gives them
    ...                      #         (every value a string), "flagged": []}
                             # return a compiled graph with a checkpointer
```

The grader calls `graph.invoke({"messages": [HumanMessage(text)]}, config)`, and while the result
has `__interrupt__` it resumes with `Command(resume="yes" or "no")`. It reads
`result["structured_response"]`. The model is scripted (no API key): it calls your tools by name
and gives the final answer by calling a tool named `Finding`.

## Part 2: the evaluation

Write `evaluate.py`. Running `python evaluate.py` classifies the topic of each post in `labels.csv`
with an LLM and prints per-topic precision and recall and a confusion matrix, then a short note on
what the errors show (which topics are confused, in which languages, and why). With no API key it
must still run, using a fake or stand-in model; a real model is optional, chosen by an environment
variable you name in your README. The grader imports these three functions:

```python
def classify_topic(llm, text) -> str:
    # one structured call: llm.with_structured_output(Topic), where Topic has one field `topic`
    # (one of the four topics); returns that topic. The grader's scripted model answers by calling
    # a tool named `Topic`.

def confusion_matrix(gold, pred, topics) -> list[list[int]]:
    # rows are gold topics, columns predicted topics, both in the order of `topics`

def per_topic_metrics(gold, pred, topics) -> dict[str, dict]:
    # {topic: {"precision": float, "recall": float, "support": int}} for every topic in `topics`;
    # support = number of gold labels of that topic
```

Rules: precision = true positives / times predicted, recall = true positives / gold count; when a
denominator is 0 the value is `0.0`. Values are not rounded (the grader allows 1e-6). Both
metric functions raise `ValueError` when `gold` and `pred` differ in length or when any label
is not one of `topics`.

## Graded on

All grader cases pass, hidden ones included; your own tests, one per rule above; the evaluation's
printed report and your note on the errors; the planning package in `docs/` (PRD.md, MODEL.md,
DECISIONS.md, as the kit's templates describe); a README with Run it, Approach, Design decisions,
AI use and Limitations; a clear, honest account of how you used the AI chat.
