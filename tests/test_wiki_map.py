"""Drift check for the kit's system model (wiki/index.md): every relative link resolves to a file."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki" / "index.md"


def test_every_wiki_link_resolves():
    links = re.findall(r"\]\(([^)#:]+)(?:#[^)]*)?\)", WIKI.read_text(encoding="utf-8"))
    assert len(links) > 10, "the Map table should link the kit's parts"
    missing = [l for l in links if not (WIKI.parent / l).exists()]
    assert missing == [], f"wiki/index.md links files that do not exist: {missing}"
