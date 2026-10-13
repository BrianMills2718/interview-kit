"""Reference evaluation. Do not open it during a practice run.

Classifies the labelled posts' topics and reports per-topic precision, recall and a confusion matrix.
usage: python evaluate.py      (offline stand-in model; set EVAL_MODEL=openai:gpt-4o-mini or similar for a real one)
"""

import csv
import os
import sys
from pathlib import Path
from typing import Literal

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from pydantic import BaseModel

TOPICS = ["transport", "weather", "sports", "prices"]
DATA = Path(__file__).resolve().parent.parent


class Topic(BaseModel):
    """The one topic a post is about."""

    topic: Literal["transport", "weather", "sports", "prices"]


def _check(gold, pred, topics):
    """Raise ValueError for unequal lengths or any label outside topics (fail loudly, never skip a row)."""
    if len(gold) != len(pred):
        raise ValueError(f"gold has {len(gold)} labels, pred has {len(pred)}")
    for label in list(gold) + list(pred):
        if label not in topics:
            raise ValueError(f"label {label!r} is not one of {topics}")


def confusion_matrix(gold, pred, topics):
    """Rows are gold topics, columns predicted topics, both in the order of topics."""
    _check(gold, pred, topics)
    index = {t: i for i, t in enumerate(topics)}
    m = [[0] * len(topics) for _ in topics]
    for g, p in zip(gold, pred):
        m[index[g]][index[p]] += 1
    return m


def per_topic_metrics(gold, pred, topics):
    """Precision, recall and support per topic; 0.0 when a denominator is zero (sklearn's zero_division=0)."""
    m = confusion_matrix(gold, pred, topics)
    out = {}
    for i, t in enumerate(topics):
        tp = m[i][i]
        predicted = sum(row[i] for row in m)
        actual = sum(m[i])
        out[t] = {"precision": tp / predicted if predicted else 0.0,
                  "recall": tp / actual if actual else 0.0,
                  "support": actual}
    return out


def classify_topic(llm, text):
    """Ask the model for the post's topic as a validated Topic; returns the topic string."""
    prompt = (f"Which topic is this post about: {', '.join(TOPICS)}? The post may be in English, "
              f"Spanish or Russian.\n\nPost: {text}")
    return llm.with_structured_output(Topic).invoke(prompt).topic


KEYWORDS = {  # the stand-in model's guesses; checked in this order, so mixed posts go to the first match
    "transport": ["bus", "metro", "traffic", "road", "train", "autobús", "metro", "tráfico", "tren",
                  "автобус", "метро", "дорог", "поезд"],
    "weather": ["rain", "storm", "degrees", "lluvia", "tormenta", "grados", "дождь", "шторм", "градус"],
    "sports": ["match", "team", "final", "partido", "equipo", "final", "матч", "команда", "финал"],
    "prices": ["cost", "price", "rent", "fare", "cuesta", "alquiler", "cara", "sube", "подорож", "аренда", "цены"],
}


class StandIn(GenericFakeChatModel):
    """Offline stand-in for a real model: answers each prompt by keywords, as a Topic tool call."""

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        text = str(messages[-1].content).split("Post:", 1)[-1].lower()
        topic = next((t for t, words in KEYWORDS.items() if any(w in text for w in words)), "prices")
        self.messages = iter([AIMessage(content="", tool_calls=[{"name": "Topic", "args": {"topic": topic}, "id": "t"}])])
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


def build_llm():
    """EVAL_MODEL names a real chat model (needs its API key); unset means the offline stand-in."""
    name = os.environ.get("EVAL_MODEL")
    if not name:
        return StandIn(messages=iter([]))
    from langchain.chat_models import init_chat_model
    return init_chat_model(name, temperature=0)


def main():
    """Classify every labelled post, print metrics and the confusion matrix."""
    posts = {r["post_id"]: r for r in csv.DictReader(open(DATA / "posts.csv", encoding="utf-8"))}
    labels = list(csv.DictReader(open(DATA / "labels.csv", encoding="utf-8")))
    llm = build_llm()
    gold = [r["topic"] for r in labels]
    pred = [classify_topic(llm, posts[r["post_id"]]["text"]) for r in labels]
    metrics = per_topic_metrics(gold, pred, TOPICS)
    print(f"{'topic':<10} precision recall support")
    for t, m in metrics.items():
        print(f"{t:<10} {m['precision']:9.2f} {m['recall']:6.2f} {m['support']:7d}")
    print("confusion (rows gold, columns predicted):", TOPICS)
    for t, row in zip(TOPICS, confusion_matrix(gold, pred, TOPICS)):
        print(f"{t:<10} {row}")
    wrong = [(r["post_id"], g, p) for r, g, p in zip(labels, gold, pred) if g != p]
    print(f"{len(wrong)} of {len(gold)} wrong; first five:", wrong[:5])
    return 0


if __name__ == "__main__":
    sys.exit(main())
