from __future__ import annotations

from change_passport.behavior_signals import (
    behavior_signal_evidence,
    extract_behavior_signals,
)


PATCH = """diff --git a/src/package/worker.py b/src/package/worker.py
index 1111111..2222222 100644
--- a/src/package/worker.py
+++ b/src/package/worker.py
@@ -1,7 +1,12 @@ def execute(item):
-def execute(item):
+def execute(item, *, strict=False):
     if item.ready:
         return 0
+    if strict:
+        raise StaleItemError(item.name)
     return 0

 def main(item):
+    if not item.ready:
+        return 2
     return execute(item)
"""


def test_extracts_generic_stop_failure_and_signature_signals():
    signals = extract_behavior_signals(PATCH)

    assert [(item.kind, item.path, item.symbol) for item in signals] == [
        ("added_exception_raise", "src/package/worker.py", "execute"),
        ("added_nonzero_return", "src/package/worker.py", "main"),
        ("changed_callable_signature", "src/package/worker.py", "execute"),
    ]
    assert signals[0].condition == "strict"
    assert signals[1].condition == "not item.ready"


def test_behavior_evidence_keeps_claim_boundaries_explicit():
    evidence = behavior_signal_evidence(
        PATCH,
        patch_sha256="abc123",
        patch_truncated=True,
    )

    assert [item["id"] for item in evidence] == [
        "git.behavior.001",
        "git.behavior.002",
        "git.behavior.003",
    ]
    assert all(item["authority"] == "git_fact" for item in evidence)
    assert all("does not prove reachability" in item["limitations"][1] for item in evidence)
    assert all("coverage is incomplete" in item["limitations"][2] for item in evidence)


def test_hunk_context_resets_symbol_instead_of_leaking_from_previous_hunk():
    patch = """diff --git a/src/package/worker.py b/src/package/worker.py
--- a/src/package/worker.py
+++ b/src/package/worker.py
@@ -1,3 +1,4 @@ def first():
 def first():
+    raise FirstError()
@@ -20,3 +21,5 @@ def second():
 def second():
+    if unavailable:
+        return 3
"""

    signals = extract_behavior_signals(patch)

    assert [(item.kind, item.symbol) for item in signals] == [
        ("added_exception_raise", "first"),
        ("added_nonzero_return", "second"),
    ]
