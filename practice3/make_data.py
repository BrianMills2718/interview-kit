"""Generate practice3's synthetic posts.csv and labels.csv, seeded, so every planted signal is reproducible.

usage: python practice3/make_data.py [out_dir]      (default: rewrites both files next to this script)

Everything here is invented: accounts are A01..A40, texts come from small templates in three languages.
Planted signals, each with a known answer the grader relies on:
- volume spikes on 2026-03-12 (a storm) and 2026-03-21 (a cup final); 2026-03-25 has no posts (feed outage);
- a coordinated group: five ru accounts post one text, varied only in case and spacing, within 4 minutes on
  2026-03-08 (one of them twice); a sixth account posts the same text a week later (not coordinated);
- a near miss: four es accounts post one text, the fourth 10 minutes after the first, on 2026-03-17;
- reply network: A03 receives the most replies, A05 and A11 tie behind it, A20 replies to itself a lot;
- es posts get more shares on average than en and ru.
Do not read this file before a practice run: it gives the answers away.
"""

import csv
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).parent
SEED = 3
START = datetime(2026, 3, 1)
DAYS = 30
SPIKES = {12: 28, 21: 22}          # day of month -> extra posts
SPIKE_TOPIC = {12: "weather", 21: "sports"}
EMPTY_DAY = 25
TOPICS = ["transport", "weather", "sports", "prices"]
LANG_OF = {f"A{i:02d}": ("en" if i <= 20 else "es" if i <= 30 else "ru") for i in range(1, 41)}
COORDINATED = ["A34", "A35", "A36", "A37", "A38"]
NEAR_MISS = ["A22", "A23", "A24", "A25"]

# Templates: the last one of each topic borrows another topic's word, so a keyword classifier errs on it.
TEXTS = {
    "en": {
        "transport": ["Bus {n} was late again this morning.", "Metro line {n} is closed for repairs.",
                      "Traffic on the ring road is terrible today.", "Fuel queue at the station on road {n}, avoid it."],
        "weather": ["Heavy rain expected tonight, take an umbrella.", "It is {n} degrees and sunny outside.",
                    "Storm warning for the coast until Friday.", "The storm cancelled the match and every bus."],
        "sports": ["Great match last night, final score {n}-1.", "Our team signed a new striker today.",
                   "Tickets for the final are sold out.", "Coach says the team trained in the rain for {n} hours."],
        "prices": ["Bread costs {n} cents more than last month.", "Rent went up again this year.",
                   "Fuel prices hit a new high today.", "Train fares rise {n} percent next month."],
    },
    "es": {
        "transport": ["El autobús {n} llegó tarde otra vez.", "La línea {n} del metro está cerrada.",
                      "Mucho tráfico en la autopista hoy.", "Cola de gasolina en la carretera {n}."],
        "weather": ["Se espera lluvia fuerte esta noche.", "Hace {n} grados y sol.",
                    "Alerta de tormenta en la costa.", "La tormenta suspendió el partido y el metro."],
        "sports": ["Gran partido anoche, {n}-1 al final.", "El equipo fichó a un nuevo delantero.",
                   "Entradas agotadas para la final.", "El equipo entrenó {n} horas bajo la lluvia."],
        "prices": ["El pan cuesta {n} céntimos más.", "El alquiler subió otra vez.",
                   "La gasolina está más cara que nunca.", "El billete de tren sube un {n} por ciento."],
    },
    "ru": {
        "transport": ["Автобус {n} снова опоздал.", "Линия метро {n} закрыта на ремонт.",
                      "На кольцевой дороге огромная пробка.", "Очередь за бензином на трассе {n}."],
        "weather": ["Ночью ожидается сильный дождь.", "Сегодня {n} градусов и солнечно.",
                    "Штормовое предупреждение на побережье.", "Шторм отменил матч и все автобусы."],
        "sports": ["Отличный матч вчера, счёт {n}:1.", "Команда подписала нового нападающего.",
                   "Билеты на финал распроданы.", "Команда тренировалась {n} часа под дождём."],
        "prices": ["Хлеб подорожал на {n} рублей.", "Аренда снова выросла.",
                   "Цены на бензин выросли до рекорда.", "Проезд в поезде подорожает на {n} процентов."],
    },
}
COORD_TEXTS = ["Мост на Северной улице закрыт навсегда, все уже знают.",
               "мост на северной улице закрыт навсегда,  все уже знают.",
               "МОСТ на Северной улице закрыт навсегда, все уже знают. ",
               "Мост на Северной  улице закрыт навсегда, все уже знают.",
               "мост на северной улице ЗАКРЫТ навсегда, все уже знают.",
               "Мост на Северной улице закрыт навсегда, все уже знают."]
NEAR_TEXTS = ["¡Los precios del pan suben otra vez! Compartid.", "¡los precios del pan suben otra vez! compartid.",
              "¡Los precios del pan  suben otra vez! Compartid.", "¡LOS PRECIOS DEL PAN SUBEN OTRA VEZ! Compartid."]
# replies received (from other accounts) by planted hubs; A20 also replies to itself SELF times
HUBS = {"A03": 14, "A05": 9, "A11": 9, "A27": 7, "A20": 3}
SELF = 8
OTHER_REPLIES = 40   # scattered replies, at most 4 received per non-hub account


def main(out_dir=HERE):
    """Build both CSVs deterministically from SEED."""
    rng = random.Random(SEED)
    accounts = sorted(LANG_OF)
    normal = [a for a in accounts if a not in COORDINATED]
    posts = []  # dicts: when, account, language, text, shares, topic, kind

    def add(when, account, text, topic, kind="normal", shares=None):
        lang = LANG_OF[account]
        if shares is None:
            shares = int(rng.expovariate(1 / (12 if lang == "es" else 8)))
        posts.append({"when": when, "account": account, "language": lang, "text": text,
                      "shares": shares, "topic": topic, "kind": kind})

    for d in range(DAYS):
        day = START + timedelta(days=d)
        if day.day == EMPTY_DAY:
            continue
        n = rng.randint(9, 14) + SPIKES.get(day.day, 0)
        for i in range(n):
            account = rng.choice(normal + ["A20"] * 3)  # A20 is a heavy poster
            spike = i >= n - SPIKES.get(day.day, 0)
            topic = SPIKE_TOPIC[day.day] if spike else rng.choice(TOPICS)
            text = rng.choice(TEXTS[LANG_OF[account]][topic]).format(n=rng.randint(2, 40))
            when = day + timedelta(minutes=rng.randint(7 * 60, 22 * 60 + 59))
            add(when, account, text, topic)

    t0 = datetime(2026, 3, 8, 14, 2)
    for offset, account, text in zip([0, 1, 1, 2, 3, 4], ["A34", "A35", "A36", "A36", "A37", "A38"], COORD_TEXTS):
        add(t0 + timedelta(minutes=offset), account, text, "transport", "coordinated", shares=0)
    add(datetime(2026, 3, 15, 10, 0), "A39", COORD_TEXTS[0], "transport", "echo", shares=1)
    t1 = datetime(2026, 3, 17, 15, 30)
    for offset, account, text in zip([0, 1, 2, 10], NEAR_MISS, NEAR_TEXTS):
        add(t1 + timedelta(minutes=offset), account, text, "prices", "near_miss", shares=0)

    posts.sort(key=lambda p: (p["when"], p["account"], p["text"]))
    for i, p in enumerate(posts, 1):
        p["post_id"] = f"P{i:04d}"
        p["reply_to"] = ""

    # Replies: a reply is a later normal post by another account (or the same, for A20's self-replies).
    def reply(target, self_reply=False):
        """Point one free normal post at an earlier post by target; return False if none fits."""
        candidates = [p for p in posts if p["kind"] == "normal" and not p["reply_to"]
                      and (p["account"] == target) == self_reply
                      and any(q["account"] == target and q["when"] < p["when"] and q is not p for q in posts)]
        if not candidates:
            return False
        p = rng.choice(candidates)
        earlier = [q for q in posts if q["account"] == target and q["when"] < p["when"] and q is not p]
        p["reply_to"] = rng.choice(earlier)["post_id"]
        return True

    for _ in range(SELF):
        assert reply("A20", self_reply=True)
    for hub, count in HUBS.items():
        for _ in range(count):
            assert reply(hub)
    received = {a: 0 for a in accounts}
    for _ in range(OTHER_REPLIES):
        target = rng.choice([a for a in normal if a not in HUBS and received[a] < 4])
        if reply(target):
            received[target] += 1

    with open(Path(out_dir) / "posts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["post_id", "date", "account_id", "language", "text", "shares", "reply_to"])
        for p in posts:
            w.writerow([p["post_id"], p["when"].strftime("%Y-%m-%d %H:%M"), p["account"], p["language"],
                        p["text"], p["shares"], p["reply_to"]])

    # 60 gold labels, 15 per topic, from normal posts only, every language represented
    labelled = []
    for topic in TOPICS:
        pool = [p for p in posts if p["kind"] == "normal" and p["topic"] == topic]
        labelled += rng.sample(pool, 15)
    labelled.sort(key=lambda p: p["post_id"])
    with open(Path(out_dir) / "labels.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["post_id", "topic"])
        for p in labelled:
            w.writerow([p["post_id"], p["topic"]])
    print(f"wrote {len(posts)} posts and {len(labelled)} labels")


if __name__ == "__main__":
    main(*sys.argv[1:2])
