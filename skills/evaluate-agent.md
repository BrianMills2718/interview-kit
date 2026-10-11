# Skill: test and evaluate an agent

Use when the solution includes an LLM or agent and needs to show it works.

## Two layers

1. **Deterministic tests (pytest, offline).** Replace the model with a fake that returns
   scripted messages, so the graph logic, tool routing and error handling are tested exactly:

   ```python
   from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
   from langchain_core.messages import AIMessage

   class FakeToolModel(GenericFakeChatModel):
       def bind_tools(self, tools, **kwargs):
           return self  # tools are ignored; replies are scripted

   llm = FakeToolModel(messages=iter([
       AIMessage("", tool_calls=[{"name": "lookup_order", "args": {"order_id": "A-100"}, "id": "1"}]),
       AIMessage("Order A-100 has shipped."),
   ]))
   ```

   Assert on membership, not counts: the right tool was called with the right arguments, and
   the final answer contains the fact the tool returned.

2. **Live evaluation (a small table).** 5-10 questions with known answers, including:
   one needing no tool, one needing two tools, one with bad input, one the agent should refuse
   or say "I don't know". Print a table: question, expected, got, pass/fail, tools used.

## Reading results

- For each failure, look at the full message trace (every tool call, its arguments, what came
  back), then classify: the tool never returned the needed fact, it returned it but the model
  ignored it, or the expected answer was wrong.
- Report pass/fail per case and the trace finding, not just an accuracy number.
