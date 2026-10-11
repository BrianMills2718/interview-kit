# Practice problem: order-support agent (2 hours)

A timed rehearsal for an agentic-AI take-home. Target 2 hours, hard stop at 4.

## How to run the practice

1. New empty folder, `git init`, then `git clone <this kit> kit` inside it.
2. `rm -rf kit/practice/reference` before reading anything else (it holds the answer).
3. Start a timer. Use only the kit's files and one AI chat, as the IDE would allow.
4. Done = `python kit/practice/grade.py solution.py` exits 0 and `bash kit/check.sh --final` exits 0.
5. Write down the elapsed time and every place you got stuck.

## The task

Build a customer-support agent for a small shop, with LangGraph or LangChain, in
`solution.py`. Data is in `kit/practice/data.json` (orders, policies, and the date to treat as today).

The agent answers a customer message using three tools, then gives a final structured answer.

| Tool | Does | Returns exactly |
|---|---|---|
| `get_order(order_id)` | look up an order | `A-101: Desk lamp, $30, delivered 2026-02-20` (date only once delivered), or `Order A-999 not found.` |
| `search_policy(query)` | find the best matching policies, best first, at most 2 | lines `P-2: <policy text>`, or `No matching policy.` |
| `request_refund(order_id, reason)` | refund if allowed | see rules below |

Refund rules, checked in this order:

1. Unknown order: `Order X not found.`
2. Already refunded: `X was already refunded.`
3. Not delivered: `Not eligible: X has not been delivered.`
4. Delivered more than 30 days before today: `Not eligible: X was delivered N days ago (limit 30).`
5. Amount over $50: pause and ask a human reviewer, before refunding. On `yes`:
   `Refunded X ($N) after approval.` Otherwise: `Refund for X declined by reviewer.`
6. Otherwise: `Refunded X ($N).`

A refund is recorded by appending the order id to `shop["refunds"]`.

The final answer is a validated `Reply`:
`category` (one of refund, shipping, damaged, other), `order_id` (`A-123` form, or none),
`action` (one sentence), `policy_ids` (list). An invalid answer goes back to the model to retry.

## Interface the grader uses

```python
def build_agent(llm, shop):   # shop = data.json as a dict, plus shop["refunds"] = []
    ...                       # return a compiled graph with a checkpointer
```

The grader calls `graph.invoke({"messages": [HumanMessage(text)]}, config)`, and while the
result has `__interrupt__` it resumes with `Command(resume="yes" or "no")`. It reads
`result["structured_response"]`. The model is scripted (no API key): it calls your tools by
name and gives the final answer by calling a tool named `Reply`.

## Graded on

All grader cases pass; your own tests; a README with Run it, Approach, Design decisions,
AI use and Limitations; a clear, honest account of how you used the AI chat.
