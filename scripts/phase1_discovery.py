"""Phase 1 discovery — get exact chunk counts for overnight run planning."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engines.excerpting.contracts import ExcerptingConfig
from engines.excerpting.src.phase1_assembly import run_phase1
from scripts.run_integration_test import load_package

PACKAGES_DIR = Path("experiments/format_diversity_test/packages")
PACKAGES = [
    "ibn_aqil_v1",
    "ibn_aqil_v3",
    "taysir",
    "ext_39_masala",
    "ext_46_qa",
]

config = ExcerptingConfig()
total_chunks = 0
large_chunks = 0

results = []

for name in PACKAGES:
    pkg_path = PACKAGES_DIR / name
    try:
        package = load_package(pkg_path)
        chunks, validation = run_phase1(package, config)

        chunk_words = [c.word_count for c in chunks]
        large = sum(1 for w in chunk_words if w > 2500)
        max_words = max(chunk_words) if chunk_words else 0

        results.append({
            "package": name,
            "content_units": len(package.content_units),
            "chunks": len(chunks),
            "large_chunks_gt2500": large,
            "max_words": max_words,
            "mean_words": round(sum(chunk_words) / len(chunk_words)) if chunk_words else 0,
        })

        total_chunks += len(chunks)
        large_chunks += large

        print(f"  {name}: {len(chunks)} chunks "
              f"(large: {large}, max: {max_words} words)")

    except Exception as exc:
        print(f"  {name}: FAILED — {exc}")
        results.append({"package": name, "error": str(exc)})

print(f"\nTotal: {total_chunks} chunks, {large_chunks} large (>2500 words)")
print(f"Estimated LLM calls: ~{total_chunks * 3} (classify + group + enrich)")
print(f"Estimated time at 131s/chunk: {total_chunks * 131 / 3600:.1f} hours")

output = Path("reference/archive/sessions/cross_provider_audit/phase1_discovery.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f"\nSaved to {output}")
