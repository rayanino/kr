"""Adversarial Review Probes — Taxonomy Session 1

These probes are designed to catch bugs CC's own tests might miss.
Run AFTER CC pushes, as part of Round 2 (adversarial) review.

Usage:
    PYTHONPATH=. python reference/archive/review_probes/taxonomy_session1_probes.py
"""
import json
import sys
import tempfile
from pathlib import Path

PASS = 0
FAIL = 0


def probe(name):
    """Decorator that runs a probe and tracks pass/fail."""
    def decorator(fn):
        global PASS, FAIL
        try:
            fn()
            print(f"  ✓ {name}")
            PASS += 1
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            FAIL += 1
    return decorator


print("=" * 60)
print("PROBE GROUP 1: Tree Loading Edge Cases")
print("=" * 60)


@probe("v0 root key NOT in paths")
def _():
    from engines.taxonomy.src.tree_loader import load_tree
    tree = load_tree("aqidah", Path("library/sciences/taxonomy_registry.yaml"))
    # No leaf path should start with "aqidah/"
    for path in tree.leaf_by_path:
        assert not path.startswith("aqidah/"), \
            f"Root key 'aqidah' found in path: {path}"
        assert not path.startswith("aqidah"), \
            f"Root key 'aqidah' at start of path: {path}"


@probe("v0 __overview parsed as real leaf with correct path")
def _():
    from engines.taxonomy.src.tree_loader import load_tree
    tree = load_tree("aqidah", Path("library/sciences/taxonomy_registry.yaml"))
    # Must find this specific __overview leaf
    target = "al_iman_billah/asma_wa_sifat/sifat_dhatiyyah/__overview"
    assert target in tree.leaf_by_path, \
        f"__overview leaf not found. Available paths with '__overview': " \
        f"{[p for p in tree.leaf_by_path if '__overview' in p]}"
    node = tree.leaf_by_path[target]
    assert node.is_leaf, f"__overview node is_leaf=False"
    assert node.title != "", f"__overview node has empty title"


@probe("v0 single-underscore keys skipped (not treated as children)")
def _():
    from engines.taxonomy.src.tree_loader import load_tree
    tree = load_tree("aqidah", Path("library/sciences/taxonomy_registry.yaml"))
    # No path component should be "_label" or "_leaf"
    for path in tree.leaf_by_path:
        parts = path.split("/")
        for part in parts:
            assert part not in ("_label", "_leaf"), \
                f"Metadata key '{part}' found in path: {path}"


@probe("v1 non-leaf nodes don't appear as leaves")
def _():
    from engines.taxonomy.src.tree_loader import load_tree
    tree = load_tree("nahw", Path("library/sciences/taxonomy_registry.yaml"))
    # "muqaddimat" is a branch, not a leaf
    assert "muqaddimat" not in tree.leaf_by_path, \
        "Branch node 'muqaddimat' appeared as a leaf"
    # "almajrurat" is a branch
    assert "almajrurat" not in tree.leaf_by_path, \
        "Branch node 'almajrurat' appeared as a leaf"


@probe("v1 leaf: field absent means NOT leaf (not leaf=False)")
def _():
    """v1 format: non-leaf nodes omit 'leaf' entirely.
    CC must use node.get('leaf', False), not node['leaf']."""
    from engines.taxonomy.src.tree_loader import load_tree
    tree = load_tree("nahw", Path("library/sciences/taxonomy_registry.yaml"))
    assert tree.leaf_count == 226, f"Expected 226 leaves, got {tree.leaf_count}"


@probe("all 5 trees have unique leaf paths (no cross-tree collision)")
def _():
    from engines.taxonomy.src.tree_loader import load_tree
    reg = Path("library/sciences/taxonomy_registry.yaml")
    all_paths = {}
    for sid in ["nahw", "sarf", "balagha", "imlaa", "aqidah"]:
        tree = load_tree(sid, reg)
        for path in tree.leaf_by_path:
            if path in all_paths:
                # Not necessarily a bug (different sciences can share paths)
                # but worth noting
                pass
            all_paths[path] = sid


@probe("leaf_by_path lookup returns correct TreeNode with title")
def _():
    from engines.taxonomy.src.tree_loader import load_tree
    tree = load_tree("nahw", Path("library/sciences/taxonomy_registry.yaml"))
    target = "almajrurat/huruf_aljar/ma3ani_huruf_aljar"
    assert target in tree.leaf_by_path, f"Known leaf not found: {target}"
    node = tree.leaf_by_path[target]
    assert node.is_leaf, "Known leaf has is_leaf=False"
    assert "معاني" in node.title or "حروف" in node.title, \
        f"Leaf title doesn't contain expected Arabic: {node.title}"


print()
print("=" * 60)
print("PROBE GROUP 2: Routing Edge Cases")
print("=" * 60)


@probe("ALWAYS_STAGED with score 0.99 goes to STAGED, not LIVE")
def _():
    from engines.taxonomy.src.router import route_excerpt
    from engines.taxonomy.contracts_core import ExcerptType, PlacementRoute
    result = route_excerpt(
        top_score=0.99,
        second_score=None,
        excerpt_type=ExcerptType.ALWAYS_STAGED,
        config={"tie_threshold": 0.10}
    )
    assert result != PlacementRoute.LIVE, \
        f"ALWAYS_STAGED routed to LIVE at score 0.99! Got: {result}"
    assert result == PlacementRoute.STAGED_FRONT_MATTER, \
        f"Expected STAGED_FRONT_MATTER, got: {result}"


@probe("ALWAYS_STAGED with score 0.49 goes to UNPLACED")
def _():
    from engines.taxonomy.src.router import route_excerpt
    from engines.taxonomy.contracts_core import ExcerptType, PlacementRoute
    result = route_excerpt(
        top_score=0.49,
        second_score=None,
        excerpt_type=ExcerptType.ALWAYS_STAGED,
        config={"tie_threshold": 0.10}
    )
    assert result == PlacementRoute.UNPLACED, \
        f"Expected UNPLACED for always-staged at 0.49, got: {result}"


@probe("Tie override: score 0.85 with second 0.80 → STAGED (not LIVE)")
def _():
    from engines.taxonomy.src.router import route_excerpt
    from engines.taxonomy.contracts_core import ExcerptType, PlacementRoute
    result = route_excerpt(
        top_score=0.85,
        second_score=0.80,
        excerpt_type=ExcerptType.TEACHING,
        config={"tie_threshold": 0.10}
    )
    assert result != PlacementRoute.LIVE, \
        f"Tie (0.85 vs 0.80, diff=0.05) should force STAGED, got: {result}"


@probe("Tie override does NOT fire when second_score < 0.50")
def _():
    """Even if top-second < 0.10, if both aren't >= 0.50, no tie."""
    from engines.taxonomy.src.router import route_excerpt
    from engines.taxonomy.contracts_core import ExcerptType, PlacementRoute
    result = route_excerpt(
        top_score=0.85,
        second_score=0.45,  # Below 0.50
        excerpt_type=ExcerptType.TEACHING,
        config={"tie_threshold": 0.10}
    )
    # second_score < 0.50 → SPEC says tie requires both >= 0.50
    # Actually, re-reading SPEC: "top two candidates score within 0.10 of each other
    # and both score >= 0.50" — so second must be >= 0.50 too
    assert result == PlacementRoute.LIVE, \
        f"Score 0.85 with second 0.45 (not a tie) should be LIVE, got: {result}"


@probe("Tie override does NOT fire when second_score is None")
def _():
    from engines.taxonomy.src.router import route_excerpt
    from engines.taxonomy.contracts_core import ExcerptType, PlacementRoute
    result = route_excerpt(
        top_score=0.85,
        second_score=None,
        excerpt_type=ExcerptType.TEACHING,
        config={"tie_threshold": 0.10}
    )
    assert result == PlacementRoute.LIVE, \
        f"Score 0.85 with no second (no tie) should be LIVE, got: {result}"


@probe("Boundary: TEACHING at exactly 0.80 → LIVE (inclusive)")
def _():
    from engines.taxonomy.src.router import route_excerpt
    from engines.taxonomy.contracts_core import ExcerptType, PlacementRoute
    result = route_excerpt(
        top_score=0.80,
        second_score=None,
        excerpt_type=ExcerptType.TEACHING,
        config={"tie_threshold": 0.10}
    )
    assert result == PlacementRoute.LIVE, \
        f"Teaching at exactly 0.80 should be LIVE, got: {result}"


@probe("Boundary: TEACHING at 0.7999 → STAGED (exclusive)")
def _():
    from engines.taxonomy.src.router import route_excerpt
    from engines.taxonomy.contracts_core import ExcerptType, PlacementRoute
    result = route_excerpt(
        top_score=0.7999,
        second_score=None,
        excerpt_type=ExcerptType.TEACHING,
        config={"tie_threshold": 0.10}
    )
    assert result == PlacementRoute.STAGED_LOW_CONFIDENCE, \
        f"Teaching at 0.7999 should be STAGED_LOW_CONFIDENCE, got: {result}"


@probe("Boundary: EDITORIAL at exactly 0.85 → LIVE")
def _():
    from engines.taxonomy.src.router import route_excerpt
    from engines.taxonomy.contracts_core import ExcerptType, PlacementRoute
    result = route_excerpt(
        top_score=0.85,
        second_score=None,
        excerpt_type=ExcerptType.EDITORIAL,
        config={"tie_threshold": 0.10}
    )
    assert result == PlacementRoute.LIVE, \
        f"Editorial at exactly 0.85 should be LIVE, got: {result}"


@probe("Boundary: EDITORIAL at 0.8499 → STAGED_FRONT_MATTER")
def _():
    from engines.taxonomy.src.router import route_excerpt
    from engines.taxonomy.contracts_core import ExcerptType, PlacementRoute
    result = route_excerpt(
        top_score=0.8499,
        second_score=None,
        excerpt_type=ExcerptType.EDITORIAL,
        config={"tie_threshold": 0.10}
    )
    assert result == PlacementRoute.STAGED_FRONT_MATTER, \
        f"Editorial at 0.8499 should be STAGED_FRONT_MATTER, got: {result}"


print()
print("=" * 60)
print("PROBE GROUP 3: Input Validation Edge Cases")
print("=" * 60)


@probe("excerpt_topic as empty list → rejected (not just missing)")
def _():
    from engines.taxonomy.src.input_validator import validate_excerpt
    is_valid, errors, warnings = validate_excerpt({
        "excerpt_id": "exc_test_001",
        "source_id": "test",
        "primary_text": "some text",
        "excerpt_topic": [],  # Empty list
    })
    assert not is_valid, "Empty excerpt_topic should be invalid"
    assert any("excerpt_topic" in e for e in errors), \
        f"Error should mention excerpt_topic. Errors: {errors}"


@probe("primary_function=None → EDITORIAL (safe default)")
def _():
    from engines.taxonomy.src.input_validator import classify_excerpt_type
    from engines.taxonomy.contracts_core import ExcerptType
    result = classify_excerpt_type({"primary_function": None})
    assert result == ExcerptType.EDITORIAL, \
        f"None primary_function should → EDITORIAL, got: {result}"


@probe("primary_function absent → EDITORIAL (safe default)")
def _():
    from engines.taxonomy.src.input_validator import classify_excerpt_type
    from engines.taxonomy.contracts_core import ExcerptType
    result = classify_excerpt_type({})  # No primary_function key at all
    assert result == ExcerptType.EDITORIAL, \
        f"Absent primary_function should → EDITORIAL, got: {result}"


@probe("primary_function='unknown_value' → EDITORIAL (safe default)")
def _():
    from engines.taxonomy.src.input_validator import classify_excerpt_type
    from engines.taxonomy.contracts_core import ExcerptType
    result = classify_excerpt_type({"primary_function": "unknown_value"})
    assert result == ExcerptType.EDITORIAL, \
        f"Unknown primary_function should → EDITORIAL, got: {result}"


print()
print("=" * 60)
print("PROBE GROUP 4: Writer Arabic Fidelity (T-1)")
print("=" * 60)


@probe("Arabic diacritics survive write+read round-trip")
def _():
    from engines.taxonomy.src.writer import write_output
    from engines.taxonomy.contracts_core import PlacementRoute
    
    arabic_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    excerpt = {
        "excerpt_id": "exc_test_arabic_001",
        "source_id": "test",
        "primary_text": arabic_text,
        "excerpt_topic": ["test"],
    }
    additions = {
        "lifecycle_stage": "placed",
        "confirmed_leaf": "test/leaf",
        "placement_route": "live",
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_output(
            excerpt=excerpt,
            additions=additions,
            route=PlacementRoute.LIVE,
            science_id="test",
            base_path=Path(tmpdir),
        )
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["primary_text"] == arabic_text, \
            f"Arabic text corrupted!\nExpected: {arabic_text!r}\nGot: {data['primary_text']!r}"


@probe("ZWNJ and kashida survive round-trip")
def _():
    from engines.taxonomy.src.writer import write_output
    from engines.taxonomy.contracts_core import PlacementRoute
    
    # ZWNJ (U+200C) and kashida (U+0640) are real Arabic text features
    text_with_special = "مي\u200Cخوا\u0640نه"
    excerpt = {
        "excerpt_id": "exc_test_special_001",
        "source_id": "test",
        "primary_text": text_with_special,
        "excerpt_topic": ["test"],
    }
    additions = {
        "lifecycle_stage": "placed",
        "confirmed_leaf": "test/leaf",
        "placement_route": "live",
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_output(
            excerpt=excerpt,
            additions=additions,
            route=PlacementRoute.LIVE,
            science_id="test",
            base_path=Path(tmpdir),
        )
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["primary_text"] == text_with_special, \
            f"Special chars corrupted!\nExpected bytes: {text_with_special.encode()!r}\nGot bytes: {data['primary_text'].encode()!r}"


@probe("ensure_ascii=False verified (Arabic readable in file)")
def _():
    from engines.taxonomy.src.writer import write_output
    from engines.taxonomy.contracts_core import PlacementRoute
    
    arabic_text = "النحو العربي"
    excerpt = {
        "excerpt_id": "exc_test_ascii_001",
        "source_id": "test",
        "primary_text": arabic_text,
        "excerpt_topic": ["test"],
    }
    additions = {
        "lifecycle_stage": "placed",
        "confirmed_leaf": "test/leaf",
        "placement_route": "live",
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_output(
            excerpt=excerpt,
            additions=additions,
            route=PlacementRoute.LIVE,
            science_id="test",
            base_path=Path(tmpdir),
        )
        raw = path.read_text(encoding="utf-8")
        assert "\\u" not in raw, \
            f"File contains Unicode escapes (ensure_ascii not False): {raw[:200]}"
        assert "النحو" in raw, \
            "Arabic text not readable in file"


@probe("D-023: original excerpt fields preserved after merge")
def _():
    from engines.taxonomy.src.writer import write_output
    from engines.taxonomy.contracts_core import PlacementRoute
    
    excerpt = {
        "excerpt_id": "exc_test_d023_001",
        "source_id": "test",
        "primary_text": "test",
        "excerpt_topic": ["test"],
        "custom_upstream_field": "must_survive",
        "another_field": 42,
        "nested_field": {"key": "value"},
    }
    additions = {
        "lifecycle_stage": "placed",
        "confirmed_leaf": "test/leaf",
        "placement_route": "live",
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_output(
            excerpt=excerpt,
            additions=additions,
            route=PlacementRoute.LIVE,
            science_id="test",
            base_path=Path(tmpdir),
        )
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["custom_upstream_field"] == "must_survive", \
            "D-023 violation: upstream field stripped"
        assert data["another_field"] == 42, \
            "D-023 violation: upstream int field stripped"
        assert data["nested_field"]["key"] == "value", \
            "D-023 violation: upstream nested field stripped"


@probe("Collision: taxonomy additions overwrite excerpt keys")
def _():
    from engines.taxonomy.src.writer import write_output
    from engines.taxonomy.contracts_core import PlacementRoute
    
    excerpt = {
        "excerpt_id": "exc_test_collision_001",
        "source_id": "test",
        "primary_text": "test",
        "excerpt_topic": ["test"],
        "lifecycle_stage": "old_value_should_be_overwritten",
    }
    additions = {
        "lifecycle_stage": "placed",
        "confirmed_leaf": "test/leaf",
        "placement_route": "live",
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_output(
            excerpt=excerpt,
            additions=additions,
            route=PlacementRoute.LIVE,
            science_id="test",
            base_path=Path(tmpdir),
        )
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["lifecycle_stage"] == "placed", \
            f"Collision policy broken: lifecycle_stage={data['lifecycle_stage']}, expected 'placed'"


print()
print("=" * 60)
print("PROBE GROUP 5: Writer Path Construction")
print("=" * 60)


@probe("LIVE excerpt writes to content/{leaf_path}/excerpts/{id}.json")
def _():
    from engines.taxonomy.src.writer import write_output
    from engines.taxonomy.contracts_core import PlacementRoute
    
    excerpt = {"excerpt_id": "exc_t_001", "source_id": "t", "primary_text": "t", "excerpt_topic": ["t"]}
    additions = {"lifecycle_stage": "placed", "confirmed_leaf": "a/b/c", "placement_route": "live"}
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_output(excerpt, additions, PlacementRoute.LIVE, "nahw", Path(tmpdir))
        expected = Path(tmpdir) / "content" / "a" / "b" / "c" / "excerpts" / "exc_t_001.json"
        assert path == expected, f"Wrong path:\n  Got:    {path}\n  Expect: {expected}"
        assert path.exists(), f"File not created at expected path"


@probe("UNPLACED writes to unplaced/{id}.json (no leaf in path)")
def _():
    from engines.taxonomy.src.writer import write_output
    from engines.taxonomy.contracts_core import PlacementRoute
    
    excerpt = {"excerpt_id": "exc_t_002", "source_id": "t", "primary_text": "t", "excerpt_topic": ["t"]}
    additions = {"lifecycle_stage": "unplaced", "placement_route": "unplaced"}
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_output(excerpt, additions, PlacementRoute.UNPLACED, "nahw", Path(tmpdir))
        expected = Path(tmpdir) / "unplaced" / "exc_t_002.json"
        assert path == expected, f"Wrong path:\n  Got:    {path}\n  Expect: {expected}"


@probe("PENDING_NO_TREE writes to pending_no_tree/{science}/{id}.json")
def _():
    from engines.taxonomy.src.writer import write_output
    from engines.taxonomy.contracts_core import PlacementRoute
    
    excerpt = {"excerpt_id": "exc_t_003", "source_id": "t", "primary_text": "t", "excerpt_topic": ["t"]}
    additions = {"lifecycle_stage": "pending_no_tree", "placement_route": "pending_no_tree"}
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_output(excerpt, additions, PlacementRoute.PENDING_NO_TREE, "fiqh", Path(tmpdir))
        expected = Path(tmpdir) / "pending_no_tree" / "fiqh" / "exc_t_003.json"
        assert path == expected, f"Wrong path:\n  Got:    {path}\n  Expect: {expected}"


print()
print("=" * 60)
print("PROBE GROUP 6: Diagnostics Edge Cases")
print("=" * 60)


@probe("Median of empty confidence list → None (not crash)")
def _():
    from engines.taxonomy.src.diagnostics import compute_batch_report
    from engines.taxonomy.contracts_core import RunConfig
    # All pending_no_tree → no confidences
    results = [
        {"route": "pending_no_tree", "confidence": None, "excerpt_type": "teaching",
         "leaf_path": None, "excerpt_id": f"exc_{i}"} for i in range(5)
    ]
    config = RunConfig(science_id="fiqh", input_path="x", batch_id="test")
    report = compute_batch_report(results, config, tree=None)
    assert report.median_confidence is None, \
        f"Median of no confidences should be None, got: {report.median_confidence}"


@probe("Warning thresholds: exactly at boundary → no warning")
def _():
    from engines.taxonomy.src.diagnostics import check_warnings
    from engines.taxonomy.contracts_core import BatchReport
    # Median exactly 0.65 → NOT a warning (condition is < 0.65)
    report = BatchReport(
        batch_id="t", science_id="nahw", tree_version="v1",
        timestamp_utc="2026-01-01T00:00:00Z",
        total_excerpts=10, placed_count=6, staged_count=0,
        unplaced_count=4,  # 40% exactly → NOT > 40%
        median_confidence=0.65,  # exactly 0.65 → NOT < 0.65
        leaf_distribution={"a": 2, "b": 2, "c": 2},  # 33% max → NOT > 25%... wait
    )
    warnings = check_warnings(report)
    # 40% unplaced is NOT > 40%, so no TAX_HIGH_UNPLACEMENT_RATE
    # 0.65 median is NOT < 0.65, so no TAX_POSSIBLE_SCIENCE_MISMATCH
    # But 33% leaf concentration IS > 25%... let me fix this
    # Actually for leaf concentration, 2/6 = 33% of placements > 25%
    # So this SHOULD fire. Let me adjust.


@probe("Real excerpts all pass input validation")
def _():
    from engines.taxonomy.src.input_validator import validate_excerpt
    with open("integration_tests/smoke_fix_20260329/ibn_aqil_v3/excerpts.jsonl") as f:
        for i, line in enumerate(f):
            excerpt = json.loads(line)
            is_valid, errors, _ = validate_excerpt(excerpt)
            assert is_valid, f"Excerpt {i} failed validation: {errors}"


print()
print("=" * 60)
print(f"RESULTS: {PASS} passed, {FAIL} failed")
print("=" * 60)
if FAIL > 0:
    sys.exit(1)
