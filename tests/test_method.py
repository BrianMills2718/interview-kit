"""The method notes: the index reaches every note, and the shipped AES plan example is accepted."""
import re, shutil, subprocess
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
METHOD = ROOT / "method"
EXAMPLE = METHOD / "aes-plan.example.yaml"


def test_readme_links_every_method_note():
    linked = set(re.findall(r"\]\(([\w.-]+\.(?:md|yaml))", (METHOD / "README.md").read_text()))
    notes = {p.name for p in METHOD.glob("*.md")} - {"README.md"}
    assert notes and notes <= linked, f"not linked from method/README.md: {sorted(notes - linked)}"
    assert all((METHOD / name).exists() for name in linked), "README links a missing file"


def _aes_project(tmp_path):
    """A committed git repo with `aes init` run, using the pinned AES revision via uvx."""
    if not shutil.which("uvx"):
        pytest.skip("uvx not installed")
    spec = subprocess.run(["bash", str(METHOD / "install_aes.sh"), "--spec"],
                          capture_output=True, text=True, check=True).stdout.strip()
    git = ["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=t", "-c", "user.email=t@t"]
    aes = ["uvx", "-q", "--from", spec, "aes"]
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(aes + ["init", "--project-id", "booking", "--actor", "a staff member",
                          "--outcome", "A staff member gets a free room booked or told why not."],
                   cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", ".aes"], cwd=tmp_path, check=True)
    subprocess.run(git + ["commit", "-qm", "init"], cwd=tmp_path, check=True)
    return aes


def test_aes_accepts_the_example_plan_and_rejects_one_without_a_disproof(tmp_path):
    aes = _aes_project(tmp_path)
    ok = subprocess.run(aes + ["plan", "validate", str(EXAMPLE)], cwd=tmp_path, capture_output=True, text=True)
    assert ok.returncode == 0 and "OK proposal PLAN-001-BOOK" in ok.stdout, ok.stdout + ok.stderr
    broken = tmp_path / "broken.yaml"
    broken.write_text(re.sub(r"\n        disproof: >\n(?:          .*\n)+", "\n", EXAMPLE.read_text()))
    assert "disproof" not in broken.read_text()
    bad = subprocess.run(aes + ["plan", "validate", str(broken)], cwd=tmp_path, capture_output=True, text=True)
    assert bad.returncode != 0 and "disproof" in bad.stdout + bad.stderr, bad.stdout + bad.stderr
