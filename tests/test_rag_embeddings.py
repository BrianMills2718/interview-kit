"""Offline tests for embedding search: a word-count embedding stands in for a real model."""

import re
import sys
from pathlib import Path

from langchain_core.embeddings import Embeddings

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from rag_embeddings import DOCS, build_store, make_search_tool  # noqa: E402

VOCAB = sorted({w for d in DOCS for w in re.findall(r"[a-z]+", d.page_content.lower())})


class WordCountEmbedding(Embeddings):
    """Vector of word counts over the documents' vocabulary: similar wording -> similar vector.

    Unlike DeterministicFakeEmbedding (a hash per exact text), a paraphrased query still lands
    near the right document, so the test checks that search actually ranks by meaning-ish overlap.
    """

    def _vec(self, text):
        words = re.findall(r"[a-z]+", text.lower())
        return [float(words.count(w)) + 1e-6 for w in VOCAB]

    def embed_documents(self, texts):
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        return self._vec(text)


def test_question_retrieves_the_matching_policy_first():
    search = make_search_tool(build_store(WordCountEmbedding()), k=2)
    out = search.invoke({"query": "how long until my refunds are issued?"})
    assert out.splitlines()[0].startswith("[refunds]")


def test_a_different_question_ranks_a_different_policy_first():
    search = make_search_tool(build_store(WordCountEmbedding()), k=1)
    out = search.invoke({"query": "can orders be cancelled before they ship?"})
    assert out.startswith("[cancel]") and len(out.splitlines()) == 1  # k=1 returns one passage
