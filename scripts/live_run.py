"""One live run of the kit's model-calling examples through OpenRouter, with every HTTP body recorded.

The examples stay route-agnostic: this script only builds clients pointed at OpenRouter and passes
them in. Each request and response body (headers dropped, so the key never reaches the file) is
appended to a JSONL trace, so a reader can see the real tool-call items, not just the final answer.

Run:  OPENROUTER_API_KEY=... uv run --with anthropic python scripts/live_run.py [trace.jsonl]
Exit status is the number of failed steps.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))

BASE = "https://openrouter.ai/api/v1"
QUESTION = "Where is order A-100?"
log = logging.getLogger("live_run")


def traced_client(trace_path: Path, label: list[str], httpx_mod=httpx):
    """HTTP client whose hooks append each request and response body to the trace file.

    httpx_mod is the client library the SDK expects: anthropic>=1.13 uses `httpx2` and rejects
    an `httpx.Client` ("Invalid `http_client` argument"); openai and langchain-openai use httpx.
    """

    def write(kind: str, body: bytes, extra: dict) -> None:
        """Append one record; bodies are JSON when they parse, text otherwise."""
        try:
            parsed = json.loads(body) if body else None
        except ValueError:
            parsed = body.decode(errors="replace")
        for item in (parsed or {}).get("data", []) if isinstance(parsed, dict) else []:
            if isinstance(item, dict) and isinstance(item.get("embedding"), (str, list)):
                item["embedding"] = f"<{len(item['embedding'])} chars/values omitted>"
        rec = {"run": label[0], "ts": time.time(), "kind": kind, **extra, "body": parsed}
        with trace_path.open("a") as f:
            f.write(json.dumps(rec, default=str) + "\n")

    def on_request(req) -> None:
        write("request", req.read(), {"method": req.method, "url": str(req.url)})

    def on_response(resp) -> None:
        write("response", resp.read(), {"status": resp.status_code, "url": str(resp.request.url)})

    client = httpx_mod.Client(timeout=120, event_hooks={"request": [on_request], "response": [on_response]})
    client.trace_path, client.label = trace_path, label  # so another library's client can share the trace
    return client


def step_openai(key, http):
    """Responses-API loop from raw_api_agent.py against an OpenAI model."""
    import openai
    from raw_api_agent import run_openai

    client = openai.OpenAI(base_url=BASE, api_key=key, http_client=http)
    answer, items = run_openai(client, QUESTION, "openai/gpt-5-mini")
    return {"answer": answer, "item_types": [getattr(i, "type", None) or i.get("type", "message") for i in items]}


def step_anthropic(key, http):
    """Messages-API loop from raw_api_agent.py against a Claude model (bearer auth, as OpenRouter expects)."""
    import anthropic
    from raw_api_agent import run_anthropic

    try:
        import httpx2  # what anthropic>=1.13 is built on
    except ImportError:
        httpx2 = httpx
    client = anthropic.Anthropic(
        base_url=BASE.removesuffix("/v1"), api_key=None, auth_token=key,
        http_client=traced_client(http.trace_path, http.label, httpx2),
    )
    answer, messages = run_anthropic(client, QUESTION, "anthropic/claude-haiku-5.5")
    return {"answer": answer, "turns": len(messages)}


def step_hardening(key, http):
    """hardening.py agent (middleware stack) with ChatOpenAI; the email must reach the model redacted."""
    from hardening import ask_with_cost, build_agent
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="openai/gpt-5-mini", base_url=BASE, api_key=key, http_client=http)
    answer, usage = ask_with_cost(build_agent(llm), QUESTION + " My email is a@b.com")
    return {"answer": answer, "usage": usage}


def step_rag(key, http):
    """rag_embeddings.py store with live embeddings; prints every document's score per query."""
    from langchain_openai import OpenAIEmbeddings
    from rag_embeddings import DOCS, build_store

    # check_embedding_ctx_length=False sends plain strings; the default sends token-id arrays.
    emb = OpenAIEmbeddings(
        model="openai/text-embedding-3-small", base_url=BASE, api_key=key,
        http_client=http, check_embedding_ctx_length=False,
    )
    store = build_store(emb)
    out = {}
    for q in ["how long do refunds take?", "when will my parcel arrive?", "can I cancel my order?"]:
        hits = store.similarity_search_with_score(q, k=len(DOCS))
        out[q] = [(d.metadata["id"], round(s, 4)) for d, s in hits]
    return out


def main() -> int:
    """Run each step, print its result or exact error, and return the number of failures."""
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    for noisy in ("httpx", "openai", "anthropic", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set")
    trace = Path(sys.argv[1] if len(sys.argv) > 1 else "live_trace.jsonl")
    label = [""]
    http = traced_client(trace, label)
    failed = 0
    for name, fn in [("openai", step_openai), ("anthropic", step_anthropic),
                     ("hardening", step_hardening), ("rag", step_rag)]:
        label[0] = name
        t0 = time.time()
        try:
            result = fn(key, http)
            print(f"== {name}: OK ({time.time() - t0:.1f}s)\n{json.dumps(result, indent=1, default=str)}")
        except Exception as e:  # recorded and counted, never hidden: the trace has the bodies
            failed += 1
            print(f"== {name}: FAILED ({time.time() - t0:.1f}s) {type(e).__name__}: {e}")
    print(f"== summary: {4 - failed} passed, {failed} failed; trace {trace}")
    return failed


if __name__ == "__main__":
    sys.exit(main())
