"""The practice grader passes the reference solution and fails broken copies of it (so it can fail)."""

import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "practice"))
import grade  # noqa: E402

REFERENCE = (ROOT / "practice/reference/solution.py").read_text()


def module_from(source):
    mod = types.ModuleType("solution")
    exec(compile(source, "solution.py", "exec"), mod.__dict__)
    return mod


def failed(results):
    return sorted(name for name, problems in results if problems)


def test_reference_passes_every_case():
    results = grade.run_all(module_from(REFERENCE))
    assert len(results) == 8
    assert failed(results) == []


@pytest.mark.parametrize("broken, expect_failed", [
    # no approval step: large refunds go through without pausing
    (("APPROVAL_OVER = 50", "APPROVAL_OVER = 500"), ["large-refund-approved", "large-refund-declined"]),
    # lenient schema: an invalid category is accepted instead of retried
    (('category: Literal["refund", "shipping", "damaged", "other"]', "category: str"), ["unknown-order-and-invalid-reply"]),
    # no idempotency: the same order is refunded twice
    (('if order_id in shop["refunds"]:', "if False:"), ["refund-twice"]),
])
def test_grader_fails_a_broken_solution(broken, expect_failed):
    old, new = broken
    assert old in REFERENCE
    assert failed(grade.run_all(module_from(REFERENCE.replace(old, new)))) == expect_failed
