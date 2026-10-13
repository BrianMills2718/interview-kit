"""Maintainers: write practice3/examples.json and reference/hidden_cases.json, then run `grade.py --encode`.

Expected values are typed from the rules in PROBLEM.md and checked by reference/recompute.py, not computed by the reference."""
import json
from pathlib import Path

P3 = Path(__file__).resolve().parent.parent
T = ["transport", "weather", "sports", "prices"]
GROUP = "accounts A34,A35,A36,A37,A38; posts P0091,P0092,P0093,P0094,P0095,P0096; 2026-03-08 14:02 to 2026-03-08 14:06"
NEAR4 = "accounts A22,A23,A24,A25; posts P0233,P0234,P0235,P0236; 2026-03-17 15:30 to 2026-03-17 15:40"
COORD = ["A34", "A35", "A36", "A37", "A38"]


def call(name, **args):
    return {"tool_calls": [{"name": name, "args": args}]}


def finding(qt, answer, numbers=None, evidence=None):
    return call("Finding", question_type=qt, answer=answer, numbers=numbers or {}, evidence_post_ids=evidence or [])


def agent(name, message, script, contains, finding_expect, flagged=(), interrupted=False, absent=(), human="yes"):
    return {"name": name, "message": message, "human": human, "script": script,
            "expect": {"flagged": [list(g) for g in flagged], "interrupted": interrupted,
                       "tool_output_contains": list(contains), "tool_output_absent": list(absent),
                       "finding": finding_expect}}


examples = [
    agent("volume-spikes-and-shares",
          "Which days had unusual volume, do Spanish posts get more shares than English ones, and how many Russian posts are there?",
          [call("daily_volume_anomalies", z=2.5), call("compare_shares", lang_a="es", lang_b="en"),
           call("count_posts", language="ru"),
           finding("volume", "Volume spiked on 2026-03-12 and 2026-03-21, and Spanish posts get more shares than English ones (p 0.0008).",
                   {"spike_days": 2, "p_value": 0.0008})],
          ["2026-03-12: 41 posts, z 3.82\n2026-03-21: 35 posts, z 2.99",
           "es vs en: mean 10.67 vs 6.86, n 118 vs 213, t 3.40, p 0.0008",
           "67 posts: ru 67"],
          {"question_type": "volume", "numbers": {"spike_days": 2.0, "p_value": 0.0008}}),
    agent("coordinated-group-flagged",
          "Is anyone posting the same message in a coordinated way? Flag them if so.",
          [call("find_coordinated", window_minutes=5, min_accounts=3),
           call("flag_coordinated", account_ids=COORD, reason="same text within 4 minutes"),
           finding("coordination", "Five accounts posted the same text within four minutes and were flagged.",
                   {"accounts": 5}, ["P0091", "P0092", "P0093", "P0094", "P0095", "P0096"])],
          [GROUP + "\naccounts A22,A23,A24; posts P0233,P0234,P0235; 2026-03-17 15:30 to 2026-03-17 15:32",
           "Flagged 5 accounts after approval."],
          {"question_type": "coordination", "evidence_post_ids": ["P0091", "P0092", "P0093", "P0094", "P0095", "P0096"]},
          flagged=[COORD], interrupted=True),
    {"name": "classifier-metrics", "kind": "metrics",
     "texts": ["Storm warning for the coast until Friday.", "Bus 7 was late again this morning.",
               "Tickets for the final are sold out.", "Rent went up again this year.",
               "Our team signed a new striker today."],
     "script": [call("Topic", topic="weather"), call("Topic", topic="transport"),
                call("Topic", topic="prices"), call("Topic", topic="prices"), call("Topic", topic="sports")],
     "gold": ["weather", "transport", "sports", "prices", "sports"], "topics": T,
     "expect": {"predictions": ["weather", "transport", "prices", "prices", "sports"],
                "confusion": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]],
                "metrics": {"transport": {"precision": 1.0, "recall": 1.0, "support": 1},
                            "weather": {"precision": 1.0, "recall": 1.0, "support": 1},
                            "sports": {"precision": 1.0, "recall": 0.5, "support": 2},
                            "prices": {"precision": 0.5, "recall": 1.0, "support": 1}}}},
]

hidden = [
    agent("count-empty-filter-means-all", "How many posts are there, and how many Russian ones on 8 March?",
          [call("count_posts", language="", start="", end=""),
           call("count_posts", language="RU", start="2026-03-08", end="2026-03-08"),
           finding("count", "There are 398 posts, 7 of them Russian on 8 March.", {"total": 398})],
          ["398 posts: en 213, es 118, ru 67", "7 posts: ru 7"], {"question_type": "count"}),
    agent("count-range-matches-nothing", "How many Spanish posts on 25 March, and between 10 and 9 March?",
          [call("count_posts", language="es", start="2026-03-25", end="2026-03-25"),
           call("count_posts", language="", start="2026-03-10", end="2026-03-09"),
           finding("count", "There were none.", {"total": 0})],
          ["0 posts.\n0 posts."], {"question_type": "count"}, absent=[" posts: "]),
    agent("z-threshold-is-inclusive", "Which days have a volume z-score of at least 2.99?",
          [call("daily_volume_anomalies", z=2.992), call("daily_volume_anomalies", z=2.99),
           finding("volume", "Two days.", {"days": 2})],
          # z=2.992 must drop 2026-03-21 (its z is 2.99297, rounded 2.99); z=2.99 must keep it (at or above)
          ["2026-03-12: 41 posts, z 3.82\n2026-03-12: 41 posts, z 3.82\n2026-03-21: 35 posts, z 2.99"],
          {"question_type": "volume"}),
    agent("window-boundary", "Check the 4-minute and 9-minute windows.",
          [call("find_coordinated", window_minutes=4, min_accounts=5),
           call("find_coordinated", window_minutes=9, min_accounts=4),
           finding("coordination", "One group.", {"groups": 1}, ["P0091"])],
          [GROUP], {"question_type": "coordination"}, absent=["A22,A23,A24,A25", "No coordinated groups."]),
    agent("same-account-counts-once", "Any group of six accounts?",
          [call("find_coordinated", window_minutes=5, min_accounts=6),
           finding("count", "No group of six accounts.", {"groups": 0})],
          ["No coordinated groups."], {"question_type": "count"}),
    agent("flag-declined-records-nothing", "Flag the Russian group.",
          [call("flag_coordinated", account_ids=COORD, reason="same text"),
           finding("coordination", "The analyst declined the flag.", {"accounts": 5}, ["P0091"])],
          ["Flag declined by analyst."], {"question_type": "coordination"}, interrupted=True, human="no",
          absent=["after approval"]),
    agent("flag-input-checked-before-pause", "Flag A34 with A99, then A34 alone, then the group twice.",
          [call("flag_coordinated", account_ids=["A34", "A99"], reason="x"),
           call("flag_coordinated", account_ids=["A34", "A34"], reason="x"),
           call("flag_coordinated", account_ids=COORD, reason="x"),
           call("flag_coordinated", account_ids=list(reversed(COORD)), reason="x"),
           finding("coordination", "One group flagged.", {"accounts": 5}, ["P0091"])],
          ["Account A99 not found.", "A group needs at least 2 accounts.", "Flagged 5 accounts after approval.",
           "Group already flagged."],
          {"question_type": "coordination"}, flagged=[COORD], interrupted=True),
    agent("hub-ties-by-account-id", "Top five reply hubs?",
          [call("top_reply_hubs", k=5), finding("network", "A03 receives the most replies.", {"A03": 14})],
          ["A03 14 replies\nA05 9 replies\nA11 9 replies\nA27 7 replies\nA04 4 replies"],
          {"question_type": "network"}, absent=["A22 4 replies"]),
    agent("self-replies-not-counted", "Top seven reply hubs?",
          [call("top_reply_hubs", k=7), call("top_reply_hubs", k=0),
           finding("network", "A03 receives the most replies.", {"A03": 14})],
          ["A27 7 replies\nA04 4 replies\nA22 4 replies\nA20 3 replies", "k must be at least 1."],
          {"question_type": "network"}),
    agent("coordination-finding-needs-evidence", "Is there coordination?",
          [call("find_coordinated", window_minutes=5, min_accounts=5),
           finding("coordination", "Five accounts posted the same text.", {"accounts": 5}),
           finding("coordination", "Five accounts posted the same text.", {"accounts": 5}, ["P0091", "P0096"])],
          [GROUP], {"question_type": "coordination", "evidence_post_ids": ["P0091", "P0096"]}),
    {"name": "precision-zero-division", "kind": "metrics", "topics": T,
     "gold": ["transport", "transport", "weather", "sports", "sports", "prices"],
     "pred": ["transport", "weather", "weather", "sports", "transport", "weather"],
     "expect": {"confusion": [[1, 1, 0, 0], [0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 0]],
                "metrics": {"transport": {"precision": 0.5, "recall": 0.5, "support": 2},
                            "weather": {"precision": 1 / 3, "recall": 1.0, "support": 1},
                            "sports": {"precision": 1.0, "recall": 0.5, "support": 2},
                            "prices": {"precision": 0.0, "recall": 0.0, "support": 1}}}},
    {"name": "prediction-outside-topics-raises", "kind": "metrics", "topics": T,
     "gold": ["transport", "weather"], "pred": ["transport", "politics"],
     "expect": {"raises": "ValueError"}},
]

(P3 / "examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
(P3 / "reference" / "hidden_cases.json").write_text(json.dumps(hidden, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(len(examples), "examples,", len(hidden), "hidden")
