"""Reference solution. Do not open it during a practice run; it exists so tests can prove the grader passes and fails."""

import re
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Literal

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from pydantic import BaseModel, Field, field_validator, model_validator
from scipy import stats

LANGUAGES = ("en", "es", "ru")


class Finding(BaseModel):
    """Final answer to the analyst's question."""

    question_type: Literal["count", "volume", "coordination", "shares", "network"]
    answer: str = Field(description="the answer in one sentence ending with a full stop")
    numbers: dict[str, float] = Field(default_factory=dict, description="the key figures, by name")
    evidence_post_ids: list[str] = Field(default_factory=list, description="post ids such as P0042")

    @field_validator("answer")
    @classmethod
    def one_sentence(cls, v):
        if not v.strip() or "\n" in v or not v.rstrip().endswith("."):
            raise ValueError("answer must be one line ending with a full stop")
        return v

    @model_validator(mode="after")
    def coordination_needs_evidence(self):
        if any(not re.fullmatch(r"P\d{4}", p) for p in self.evidence_post_ids):
            raise ValueError("evidence ids look like P0042")
        if self.question_type == "coordination" and not self.evidence_post_ids:
            raise ValueError("a coordination finding needs at least one evidence post id")
        return self


def _normalise(text):
    """Lower-case and collapse runs of whitespace, so case and spacing tricks do not hide copies."""
    return " ".join(text.lower().split())


def build_agent(llm, data):
    posts = [dict(p, when=datetime.strptime(p["date"], "%Y-%m-%d %H:%M"), shares=int(p["shares"]))
             for p in data["posts"]]
    by_id = {p["post_id"]: p for p in posts}
    accounts = {p["account_id"] for p in posts}

    @tool
    def count_posts(language: str = "", start: str = "", end: str = "") -> str:
        """Count posts by language and date range (YYYY-MM-DD, inclusive); an empty string means no filter."""
        lang = language.lower()
        if lang and lang not in LANGUAGES:
            return f"Unknown language: {language}."
        bounds = []
        for d in (start, end):
            try:
                bounds.append(date.fromisoformat(d) if d else None)
            except ValueError:
                return f"Invalid date: {d}."
        lo, hi = bounds
        hits = Counter(p["language"] for p in posts
                       if (not lang or p["language"] == lang)
                       and (lo is None or p["when"].date() >= lo) and (hi is None or p["when"].date() <= hi))
        if not hits:
            return "0 posts."
        parts = ", ".join(f"{l} {hits[l]}" for l in LANGUAGES if hits[l])
        return f"{sum(hits.values())} posts: {parts}"

    @tool
    def daily_volume_anomalies(z: float) -> str:
        """Days whose post count has a z-score (rounded to 2 decimals) at or above z, zero-post days included."""
        per_day = Counter(p["when"].date() for p in posts)
        first, last = min(per_day), max(per_day)
        days = [first + timedelta(days=i) for i in range((last - first).days + 1)]
        counts = [per_day[d] for d in days]
        mean, std = statistics.fmean(counts), statistics.pstdev(counts)  # population std, as the spec says
        if std == 0:
            return "No anomalous days."
        lines = []
        for d, c in zip(days, counts):
            score = round((c - mean) / std, 2)
            if score >= z:
                lines.append(f"{d.isoformat()}: {c} posts, z {score:.2f}")
        return "\n".join(lines) or "No anomalous days."

    @tool
    def find_coordinated(window_minutes: int, min_accounts: int) -> str:
        """Groups of posts with the same normalised text from at least min_accounts distinct accounts within the window."""
        by_text = defaultdict(list)
        for p in sorted(posts, key=lambda p: (p["when"], p["post_id"])):
            by_text[_normalise(p["text"])].append(p)
        groups = []
        for same in by_text.values():
            i = 0
            while i < len(same):
                anchor = same[i]["when"]
                window = [p for p in same[i:] if p["when"] - anchor <= timedelta(minutes=window_minutes)]
                if len({p["account_id"] for p in window}) >= min_accounts:
                    groups.append(window)
                    i += len(window)  # next anchor: the first post after the group
                else:
                    i += 1
        groups.sort(key=lambda g: (g[0]["when"], g[0]["post_id"]))
        lines = [f"accounts {','.join(sorted({p['account_id'] for p in g}))}; "
                 f"posts {','.join(p['post_id'] for p in g)}; "
                 f"{g[0]['date']} to {g[-1]['date']}" for g in groups]
        return "\n".join(lines) or "No coordinated groups."

    @tool
    def compare_shares(lang_a: str, lang_b: str) -> str:
        """Welch's t-test on shares between two languages' posts (scipy, unequal variances)."""
        a_l, b_l = lang_a.lower(), lang_b.lower()
        for given, l in ((lang_a, a_l), (lang_b, b_l)):
            if l not in LANGUAGES:
                return f"Unknown language: {given}."
        if a_l == b_l:
            return "Pick two different languages."
        a = [p["shares"] for p in posts if p["language"] == a_l]
        b = [p["shares"] for p in posts if p["language"] == b_l]
        if len(a) < 2 or len(b) < 2:
            return "Not enough posts."
        t, p = stats.ttest_ind(a, b, equal_var=False)
        return (f"{a_l} vs {b_l}: mean {statistics.fmean(a):.2f} vs {statistics.fmean(b):.2f}, "
                f"n {len(a)} vs {len(b)}, t {t:.2f}, p {p:.4f}")

    @tool
    def top_reply_hubs(k: int) -> str:
        """Accounts that receive the most replies from other accounts, most first, ties by account id."""
        if k < 1:
            return "k must be at least 1."
        received = Counter()
        for p in posts:
            target = by_id.get(p["reply_to"]) if p["reply_to"] else None
            if target and target["account_id"] != p["account_id"]:  # a reply to oneself is not a link
                received[target["account_id"]] += 1
        ranked = sorted(received.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
        return "\n".join(f"{a} {n} replies" for a, n in ranked) or "No replies."

    @tool
    def flag_coordinated(account_ids: list[str], reason: str) -> str:
        """Flag a group of accounts as coordinated. An analyst must approve before anything is recorded."""
        group = sorted(set(account_ids))
        if len(group) < 2:
            return "A group needs at least 2 accounts."
        for a in account_ids:
            if a not in accounts:
                return f"Account {a} not found."
        if group in data["flagged"]:
            return "Group already flagged."
        answer = interrupt({"accounts": group, "reason": reason})
        if str(answer).strip().lower() != "yes":
            return "Flag declined by analyst."
        data["flagged"].append(group)
        return f"Flagged {len(group)} accounts after approval."

    return create_agent(llm, tools=[count_posts, daily_volume_anomalies, find_coordinated, compare_shares,
                                    top_reply_hubs, flag_coordinated],
                        response_format=ToolStrategy(Finding), checkpointer=InMemorySaver(),
                        system_prompt="You analyse social posts with tools. Compute before you claim; "
                                      "cite the post ids you relied on.")
