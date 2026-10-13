"""Recompute the hidden and shown expected values from posts.csv by plain arithmetic, without the reference.

usage: python practice3/reference/recompute.py
A second, independent route to the numbers in examples.json and hidden_cases.json: if this and the
reference disagree, one of them misreads a rule. Welch's t and degrees of freedom are written out
by hand; only the t distribution's tail comes from scipy.
"""

import csv
import math
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from scipy.stats import t as t_dist

rows = list(csv.DictReader(open(Path(__file__).resolve().parent.parent / "posts.csv", encoding="utf-8")))
when = {r["post_id"]: datetime.strptime(r["date"], "%Y-%m-%d %H:%M") for r in rows}

print("total", len(rows), dict(sorted(Counter(r["language"] for r in rows).items())))
print("ru on 2026-03-08", sum(r["language"] == "ru" and r["date"].startswith("2026-03-08") for r in rows))
print("es on 2026-03-25", sum(r["language"] == "es" and r["date"].startswith("2026-03-25") for r in rows))

# daily volume: every calendar day from the first to the last, zero days included; population std
day_counts = Counter(r["date"][:10] for r in rows)
d0, d1 = datetime.strptime(min(day_counts), "%Y-%m-%d"), datetime.strptime(max(day_counts), "%Y-%m-%d")
days = [(d0 + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((d1 - d0).days + 1)]
counts = [day_counts.get(d, 0) for d in days]
mean = sum(counts) / len(counts)
std = math.sqrt(sum((c - mean) ** 2 for c in counts) / len(counts))
print("days", len(days), "zero days", [d for d, c in zip(days, counts) if c == 0], f"mean {mean:.4f} std {std:.4f}")
for d, c in zip(days, counts):
    if (c - mean) / std > 2:
        print(f"  {d}: {c} posts, z {(c - mean) / std:.4f}")

# Welch: t = (ma - mb) / sqrt(va/na + vb/nb), sample variances; Welch-Satterthwaite df; two-sided p
for a, b in (("es", "en"), ("en", "ru")):
    xa = [int(r["shares"]) for r in rows if r["language"] == a]
    xb = [int(r["shares"]) for r in rows if r["language"] == b]
    ma, mb = sum(xa) / len(xa), sum(xb) / len(xb)
    va = sum((x - ma) ** 2 for x in xa) / (len(xa) - 1)
    vb = sum((x - mb) ** 2 for x in xb) / (len(xb) - 1)
    se2 = va / len(xa) + vb / len(xb)
    tval = (ma - mb) / math.sqrt(se2)
    df = se2 ** 2 / ((va / len(xa)) ** 2 / (len(xa) - 1) + (vb / len(xb)) ** 2 / (len(xb) - 1))
    print(f"{a} vs {b}: mean {ma:.2f} vs {mb:.2f}, n {len(xa)} vs {len(xb)}, t {tval:.2f}, df {df:.1f}, p {2 * t_dist.sf(abs(tval), df):.4f}")

# identical normalised texts by 2+ accounts within 10 minutes of each other (pairwise), to see the planted groups
norm = {}
for r in rows:
    norm.setdefault(" ".join(r["text"].lower().split()), []).append(r)
for text, rs in norm.items():
    rs = sorted(rs, key=lambda r: when[r["post_id"]])
    span = (when[rs[-1]["post_id"]] - when[rs[0]["post_id"]]).total_seconds() / 60
    if len({r["account_id"] for r in rs}) >= 3 and span <= 60 * 24 * 10:
        print("same text", len(rs), "posts", sorted({r["account_id"] for r in rs}),
              [(r["post_id"], r["date"][5:]) for r in rs])

# replies received, self-replies excluded and included
author = {r["post_id"]: r["account_id"] for r in rows}
other = Counter(author[r["reply_to"]] for r in rows if r["reply_to"] and author[r["reply_to"]] != r["account_id"])
both = Counter(author[r["reply_to"]] for r in rows if r["reply_to"])
print("replies received (others only)", sorted(other.items(), key=lambda kv: (-kv[1], kv[0]))[:8])
print("replies received (self included)", sorted(both.items(), key=lambda kv: (-kv[1], kv[0]))[:3])
