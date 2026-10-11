"""Document search with embeddings: a vector store as an agent tool.

Uses LangChain's in-memory vector store (no server, no extra install). Swap the embedding for a
real one when live; tests use a deterministic fake so they run offline. For many documents,
FAISS (`pip install faiss-cpu`, `langchain_community.vectorstores.FAISS`) is the drop-in next step.

Run live:  OPENAI_API_KEY=... python examples/rag_embeddings.py "how long do refunds take?"
Test:      pytest tests/test_rag_embeddings.py -v
"""

import logging
import sys

from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore

log = logging.getLogger("rag")

DOCS = [
    Document("Refunds are issued within 5 business days of receiving the return.", metadata={"id": "refunds"}),
    Document("Standard shipping takes 3 to 7 days; express takes 1 to 2 days.", metadata={"id": "shipping"}),
    Document("Orders can be cancelled free of charge until they ship.", metadata={"id": "cancel"}),
]


def build_store(embeddings, docs=DOCS) -> InMemoryVectorStore:
    """Embed the documents once and keep them in memory for similarity search."""
    store = InMemoryVectorStore(embeddings)
    store.add_documents(docs)
    return store


def make_search_tool(store, k: int = 2):
    """Wrap the store as a tool; results carry their source id so answers can cite it."""

    @tool
    def search_policies(query: str) -> str:
        """Search the store policy documents. Use for any question about refunds, shipping or
        cancellations. Returns up to k passages, each prefixed with its [source id]."""
        hits = store.similarity_search_with_score(query, k=k)
        log.info("search %r -> %s", query, [(d.metadata["id"], round(s, 3)) for d, s in hits])
        if not hits:
            return "No matching policy found."
        return "\n".join(f"[{d.metadata['id']}] {d.page_content}" for d, _ in hits)

    return search_policies


if __name__ == "__main__":
    from langchain_openai import OpenAIEmbeddings

    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    tool_ = make_search_tool(build_store(OpenAIEmbeddings(model="text-embedding-3-small")))
    print(tool_.invoke({"query": " ".join(sys.argv[1:]) or "how long do refunds take?"}))
