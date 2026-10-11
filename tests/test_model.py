"""Drift check for docs/model/ARCHITECTURE.md: each named writer exists and writes what the model says."""
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = (ROOT / "docs" / "model" / "ARCHITECTURE.md").read_text(encoding="utf-8")

# model row ID -> (writer file, text in the writer that does the write)
WRITERS = {
    "P1": ("build_kit.sh", "> KIT.md"),
    "P2": ("check.sh", "> .git/hooks/pre-commit"),
    "P3": ("method/install_aes.sh", "uv tool install"),
    "P4": ("practice/grade.py", "if __name__ == \"__main__\""),
}


def test_every_runtime_row_has_a_writer_that_writes_it():
    rows = set(re.findall(r"^\| (P\d+) \|", MODEL, re.M))
    assert rows == set(WRITERS), f"model runtime rows {sorted(rows)} != checked writers {sorted(WRITERS)}"
    for pid, (path, marker) in WRITERS.items():
        assert f"`{path}`" in MODEL, f"{pid}: model does not name writer {path}"
        assert marker in (ROOT / path).read_text(encoding="utf-8"), f"{pid}: {path} no longer contains {marker!r}"


def test_kit_md_matches_its_sources(tmp_path):
    for p in ["build_kit.sh", "AGENTS.md", "PLAN.template.md"]:
        shutil.copy(ROOT / p, tmp_path / p)
    for d in ["skills", "agents", "method", "templates"]:
        if (ROOT / d).exists():
            shutil.copytree(ROOT / d, tmp_path / d)
    subprocess.run(["bash", "build_kit.sh"], cwd=tmp_path, check=True, capture_output=True)
    assert (tmp_path / "KIT.md").read_text() == (ROOT / "KIT.md").read_text(), "KIT.md is stale: run ./build_kit.sh"


def test_kit_md_bundles_every_note():
    """Model V1: KIT.md is a view of every note in B1, method/ included; no note left out."""
    kit = (ROOT / "KIT.md").read_text(encoding="utf-8")
    notes = ["AGENTS.md", "PLAN.template.md"] + [
        str(p.relative_to(ROOT)) for d in ["skills", "agents", "method", "templates"] for p in sorted((ROOT / d).rglob("*.md"))
    ]
    missing = [n for n in notes if f"<!-- {n} -->" not in kit]
    assert not missing, f"KIT.md leaves out: {missing}"
