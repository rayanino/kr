# Proving excerpts reconstruct the source: a verification architecture for KR

**The right mechanism is a Round-Trip Correctness (RTC) gate that proves every book's excerpts, when concatenated in order, reproduce the normalized source text byte-for-byte.** This is computationally trivial — under 3 minutes for the entire 7,475-book corpus — and draws on a principle shared by information theory, archival science, and the Islamic scholarly tradition of muqābalah: a decomposition is trustworthy only when you can reverse it. The pipeline already verifies process integrity through D-023, FP-1–22, and the Batch Completion Gate. What it lacks is the complementary proof: that the *outputs* contain everything the *inputs* had, with nothing silently lost. This report defines exactly what "lossless decomposition" means for this pipeline, surveys how six disciplines solve the same problem, and proposes a concrete gate with schemas an engineer can build from.

---

## What "lossless" actually means for Arabic text excerpting

Three traditions converge on a single principle, each adding a necessary constraint.

In **information theory**, a decomposition D of data X is lossless if and only if H(X|D) = 0 — no uncertainty about the original remains given the parts. For a deterministic text segmentation, this simplifies to a concrete test: X must be a function of D, meaning the original can be reconstructed exactly from the excerpts. Shannon's source coding theorem tells us data can be compressed to its entropy rate but no further without loss. Excerpting is not compression — it is *partitioning* — so the bar is higher: every character must appear in exactly one excerpt.

In **archival science**, the OAIS reference model (ISO 14721) mandates that every transformation between information packages must have a "plan of reversibility." The 2012 revision explicitly requires that archives demonstrate transformations between Submission, Archival, and Dissemination Information Packages are reversible. OAIS also introduces the concept of "Transformational Information Properties" — the specific properties you *intend* to preserve through a transformation. This is the crucial insight for KR: **you must define which representation of the text is the canonical reference** before you can verify reconstruction against it.

In the **Islamic scholarly tradition**, muqābalah (مقابلة, collation) is the practice of comparing a copied text word-by-word against its exemplar to certify fidelity. Scribes marked their progress with بلاغ (balāgha) notes in margins, creating a verifiable coverage trail. Modern taḥqīq (تحقيق, critical editing) extends this with a critical apparatus documenting every variant reading. The KITAB project's passim algorithm operationalizes this digitally — splitting texts into **300-word milestones** and using Smith-Waterman alignment to verify that passages match their sources even through minor transcription errors.

The synthesis of these three traditions yields the governing principle for KR: **a decomposition is lossless when every character of the normalized source text appears in exactly one excerpt, at a known offset, and the ordered concatenation of all excerpts reproduces the normalized source identically.** This is formally equivalent to proving the excerpts form a *complete partition* of the source text — no gaps, no overlaps, no mutations. The verification is a hash comparison: SHA-256(concat(sorted_excerpts)) must equal SHA-256(normalized_source).

But there is a critical subtlety. The pipeline performs normalization *before* excerpting — converting Shamela HTML into clean text, handling Unicode forms, potentially stripping or standardizing tashkeel (diacritics), normalizing alef/hamza variants. **Reconstruction verification should target the normalized form, not the raw HTML input.** The raw-to-normalized transformation is a separate verification concern (Phase 1 integrity), while the excerpting verification (Phase 2 output) proves that *given the normalized text, nothing was lost in decomposition*.

---

## Six disciplines, one pattern: hash the whole, partition the parts

Every domain that solves this problem converges on a remarkably similar two-layer architecture: **coverage verification** (proving the parts tile the whole) plus **content verification** (proving each part is uncorrupted).

**ZFS and content-addressable storage** use Merkle trees — recursive hash structures where every block's checksum is stored in its parent's metadata, cascading up to a root hash. ZFS computes a **256-bit checksum** for every block on every read, enabling self-healing when redundant copies exist. Git and IPFS extend this with content-addressable naming: every object's identifier *is* its hash, making corruption self-evident. The Merkle property means verifying any single block requires only O(log n) hashes from leaf to root, while verifying the entire tree is O(n).

**Database theory** provides the formal framework through the *lossless join property*. A decomposition of relation R into {R1, R2, ...Rm} is lossless if and only if the natural join of all decomposed relations returns exactly the original — no spurious tuples, no missing tuples. The Chase Algorithm proves this formally. CockroachDB operationalizes it: every node runs a continuous consistency checker computing **SHA-512 checksums** of range snapshots across replicas, with a 24-hour cycle covering all data. When checksums diverge, a second pass diffs key-by-key to locate the discrepancy. This caught real bugs including protobuf serialization non-determinism — exactly the kind of subtle issue that byte-level verification catches.

**Digital forensics** chains hash verification across every custody transfer. NIST SP 800-86 mandates computing message digests "before and after bit stream imaging" at every phase: collection, examination, analysis, reporting. The principle is simple and absolute: **any transformation that changes even one bit is detected**. For KR, this means hashing the source text before excerpting, then verifying the reconstruction hash matches.

**WARC web archiving** (ISO 28500) adds an elegant refinement: **dual digests**. Each record carries both a `WARC-Block-Digest` (hash of the full record including protocol headers) and a `WARC-Payload-Digest` (hash of just the content body). This separation lets you verify content integrity independently of framing metadata — directly applicable to KR, where you want to verify the Arabic text content independently of the excerpt's metadata wrapper.

**NLP span annotation** contributes the coverage verification algorithm. The BIO (Begin-Inside-Outside) tagging scheme guarantees coverage by construction — every token gets exactly one label. For arbitrary spans, the standard verification is sorted interval validation: sort spans by start offset, verify the first starts at 0, each subsequent span's start equals the previous span's end, and the last span's end equals the document length. This runs in **O(n log n)** for the sort and O(n) for the walk.

**Archival fixity checking** (NDSA Levels of Digital Preservation) adds temporal verification — not just checking integrity at creation, but re-checking periodically. Level 3 requires checking fixity "monthly, quarterly, or yearly" because storage corruption can occur silently. For a corpus of 7,475 books maintained over years, periodic re-verification catches bit rot that single-point-in-time checks miss.

---

## The canonical normalization problem in Arabic text

The single biggest implementation challenge is not algorithmic but linguistic: **Arabic text normalization creates a gap between raw bytes and meaningful content** that makes naive byte-level verification produce catastrophic false-positive rates.

Arabic text carries diacritical marks (tashkeel: fatḥa, ḍamma, kasra, shadda, sukūn, tanwīn) that change Unicode codepoints without changing the base consonantal text. The word كتب occupies 6 bytes, but كَتَبَ occupies 12. Alef variants (أ إ آ ا) are routinely interchanged across editions and digital corpora. Tāʾ marbūṭa (ة) and hāʾ (ه) alternate at word boundaries. Kashida/tatweel (ـ) appears and disappears depending on typesetting. Without normalization-aware verification, **if the source includes diacritics but excerpts strip them, nearly 100% of excerpts would fail byte-level verification** — a false-positive catastrophe that would make the gate useless.

The solution is a **"normalize-then-hash" protocol** with a defined canonical form. The PyArabic library's `normalize_searchtext()` function provides the reference implementation, applying five ordered steps: strip tashkeel → strip tatweel → normalize hamza/alef variants → normalize lam-alef ligatures → normalize tāʾ marbūṭa and alef maqṣūra. Critically, the **same normalization function must be applied to both the source text and the reconstruction** before hashing. The normalization function itself becomes part of the verification specification — versioned, deterministic, and recorded in every verification artifact.

This creates two integrity levels that serve different purposes:

- **Canonical content integrity**: SHA-256 of the normalized form. Proves that the meaningful textual content is fully preserved. This is the primary gate.
- **Raw form preservation**: SHA-256 of the original (pre-normalization) text stored alongside excerpts. Proves that the original representation is also retained for scholarly reference, even though verification operates on the canonical form.

The OAIS concept of Transformational Information Properties formalized precisely this distinction: you must declare *what* you intend to preserve, and verify against that declaration.

---

## Computational cost is negligible — verification should be exhaustive

The numbers eliminate any argument for sampling over exhaustive verification.

**Hashing cost**: At a conservative **636 MB/s** throughput for SHA-256 on modern hardware (benchmarked on Apple M1 Pro with 1 MB blocks), hashing the entire 7,475-book corpus (~7.5 GB assuming ~1 MB average) takes approximately **12 seconds**. Hashing all ~750,000 excerpt records (~3.75 GB at ~5 KB average) takes roughly **6 seconds**. The full reconstruction verification — concatenating excerpts per book and comparing hashes — adds perhaps **60–120 seconds** for string operations. **Total verification time: under 3 minutes** for the entire corpus, which is less than 0.1% of the LLM extraction time that dominates the pipeline.

**Storage overhead**: Each excerpt needs approximately **80 bytes** of reconstruction metadata — a SHA-256 hash (64 bytes hex), source offset (4 bytes), source length (4 bytes), normalization flags (2 bytes), and verification status (1 byte), plus a book ID reference. For 750,000 excerpts, this totals roughly **60 MB**. The full verification artifact (W3C PROV-aligned JSON record per excerpt) runs about 500 bytes compressed, totaling ~375 MB for the full corpus. Both figures are negligible relative to the ~7.5 GB source corpus.

**False-positive mitigation**: With the normalize-then-hash approach, expected false-positive rates drop from near-100% (raw bytes with diacritics variation) to effectively **zero** for legitimate transformations. The remaining failure cases indicate actual data loss — exactly what the gate should catch. The normalization function must be versioned and frozen per pipeline run; changing normalization rules between excerpting and verification would produce spurious failures.

Given these costs, the recommendation is unambiguous: **run exhaustive verification on every excerpt of every book, every time.** There is no computational reason to sample. The gate adds negligible overhead while providing absolute coverage.

---

## The Reconstruction Proof Gate: architecture and placement

The gate belongs at a specific point in the pipeline — **after Phase 2 (LLM teaching unit extraction), before Phase 3 (metadata enrichment)** — because Phase 2 is where text is decomposed and information loss can occur. Phase 1 (deterministic preprocessing) is separately verifiable by its own hash chain, and Phase 3 (metadata enrichment) adds to excerpts without modifying their text content.

**Gate behavior follows Option C — the tiered approach — with a modification**: given that exhaustive verification costs under 3 minutes, *all* books get full verification, but the *response* to failures is tiered.

For the **Tier 1 production batch** (40 books): hard gate. Any single book that fails reconstruction verification halts the pipeline for that batch. The gate emits a detailed diff report showing exactly which characters are missing, duplicated, or mutated. No excerpts from that book proceed to Phase 3 until the failure is resolved. This reflects the owner's five-time, Tier 1 priority demand.

For the **full corpus** (7,475 books): soft gate with escalation. Failed books are quarantined — their excerpts are tagged with `verification_status: FAILED` and excluded from downstream synthesis, but the pipeline continues processing other books. A circuit breaker trips if more than 10% of books in any batch fail, halting the entire run on the assumption of a systematic bug rather than isolated data issues.

**What the gate checks**, in order:

1. **Coverage completeness**: Are the excerpt offsets a complete partition of the normalized source? Sort excerpts by `source_offset`, verify first starts at 0, each `source_offset[i]` equals `source_offset[i-1] + source_length[i-1]`, and the last excerpt's end equals the normalized source length. Complexity: O(n log n).

2. **Content fidelity**: Does `SHA-256(normalize(concat(sorted_excerpts)))` equal `SHA-256(normalize(source))`? This is the definitive test. Complexity: O(n).

3. **Individual excerpt integrity**: Does each excerpt's stored hash match `SHA-256(normalize(excerpt.text))`? This catches corruption of individual excerpts after initial extraction. Complexity: O(n).

If check 1 or 2 fails, the gate falls back to character-level diff to locate the exact discrepancy — a diagnostic step, not a routine verification.

---

## Concrete schema for the reconstruction proof artifact

Each book produces one `ReconstructionProof` record — the artifact that proves (or disproves) lossless decomposition:

```
ReconstructionProof:
  proof_id:              UUID
  timestamp:             ISO-8601 datetime
  pipeline_version:      string (e.g., "1.3.2")
  normalization_version: string (e.g., "pyarabic-0.6.15-nfkc-strip-tashkeel")
  
  source:
    book_id:             string (e.g., "ISL-00142")
    raw_hash:            SHA-256 of original pre-normalization text
    normalized_hash:     SHA-256 of source after canonical normalization
    normalized_length:   integer (character count)
    file_path:           string
  
  excerpts:
    count:               integer
    excerpt_manifest:    array of:
      excerpt_id:        string
      sequence_index:    integer (sort order for reconstruction)
      source_offset:     integer (character position in normalized source)
      source_length:     integer (character count)
      content_hash:      SHA-256 of normalized excerpt text
    total_coverage:      integer (sum of all source_length values)
  
  verification:
    coverage_check:      PASS | FAIL
    coverage_gaps:       array of {start, end} (empty on PASS)
    coverage_overlaps:   array of {start, end, excerpt_ids} (empty on PASS)
    reconstruction_hash: SHA-256 of concat(sorted excerpts after normalization)
    hash_match:          boolean (reconstruction_hash == source.normalized_hash)
    result:              PASS | FAIL
    failure_detail:      null | {type, location, expected, actual}
  
  gate_decision:
    tier:                1 | 2 (Tier 1 = production batch, Tier 2 = full corpus)
    action:              PROCEED | HALT | QUARANTINE
    requires_review:     boolean
```

This artifact is **the proof**. If `verification.result` is PASS and the artifact is stored alongside the excerpts, any future auditor can independently verify the claim by re-running the concatenation and hash comparison. The artifact is self-contained — it records the normalization version, the source hash, and every excerpt's offset, so verification can be reproduced even if the pipeline code changes.

---

## Recommended architecture: the complete picture

The verification mechanism is a **Round-Trip Correctness gate** implementing the concatenation-hash pattern, positioned after LLM extraction (Phase 2) and before metadata enrichment (Phase 3).

**The verification algorithm per book** executes three steps in sequence: (1) load all excerpts produced for that book, sort by `source_offset`; (2) verify the offset sequence forms a complete partition with no gaps or overlaps; (3) concatenate excerpt texts in order, apply canonical Arabic normalization, compute SHA-256, and compare against the pre-stored normalized source hash. The entire operation is O(n log n) in the number of excerpts per book and O(m) in total text length — effectively instantaneous.

**The gate behavior is tiered**: Tier 1 books (production batch) face a hard gate that halts on any failure. All other books face a soft gate that quarantines failures and continues processing. A circuit breaker halts everything if failure rate exceeds 10% of any batch.

**Each verification run produces a `ReconstructionProof` artifact** per book — a JSON record containing the source hash, the excerpt manifest with offsets and individual hashes, the coverage check result, the reconstruction hash, and the gate decision. These artifacts are stored alongside the excerpt outputs and constitute the permanent, auditable proof that the owner demanded.

**For implementation**, an engineer needs four components: (1) a canonical Arabic normalization function (wrap PyArabic's `normalize_searchtext` plus Unicode NFC, version-lock it, store the version string in every proof artifact); (2) an offset-tracking modification to Phase 2 output so every excerpt records its `source_offset` and `source_length` in the normalized text; (3) the verification function itself (~50 lines of Python: sort, walk offsets, concatenate, hash, compare); and (4) the gate wrapper that reads the verification result, applies the tier-appropriate policy, and either proceeds, halts, or quarantines. The normalization function is the only component requiring domain expertise; the rest is mechanical.

This architecture satisfies the owner's demand with mathematical certainty: if the gate passes, the excerpts *provably* reconstruct the source. If it fails, it tells you exactly where and why. The muqābalah is automated, exhaustive, and runs in seconds.