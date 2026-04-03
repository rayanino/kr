# Golden Example Benchmark — Multiresolution Book Digester

## Why this exists

This is not an implementation request by default.

It is a **gold-standard benchmark** for the kind of autonomous, out-of-the-box product reasoning the KR autonomous system should be able to originate on its own.

Owner framing on 2026-04-03:

- The owner does **not** want “creative work” to mean only low-level substitutions like “use library X instead of library Y”.
- The owner wants the system to surface ideas that materially reframe the product or knowledge model and make him say: “wow, this is genuinely smart, extremely well done”.
- The example below is the benchmark. The system should be able to generate ideas at least this strong, and ideally stronger.

## Golden example

The system should be able to produce ideas like:

- the excerpting/taxonomy environment should not only preserve the finest-grained end-node excerpts
- every level of the knowledge tree could retain content, with progressively finer granularity as the user descends
- science/top-level nodes could retain full books
- lower levels could retain chapters
- deeper levels could retain subchapters
- terminal leaves could retain the finest-grained excerpts

Owner shorthand:

- “build a proper book digester, not just a book excerpter”

## Benchmark verdict against the current live system

Current KR has **not yet reached or exceeded** this level of reasoning.

Repo-backed reasons:

- taxonomy v1 explicitly places excerpts only at leaves and never at branch nodes
- excerpting currently emits finest-grained `ExcerptRecord` objects only
- synthesis currently consumes leaf-placed excerpts only

At the same time, the repo already preserves important upstream ingredients that make this idea plausible later:

- full-book/source retention in the source layer
- hierarchical structure and division trees in normalization
- semantic granularity choice at `TeachingUnit` in excerpting Phase 2b
- preserved structural lineage like `div_id` and `div_path`

## Coworker-backed conclusions

Major-point agreement reached on 2026-04-03:

1. The idea is genuinely strong and non-trivial relative to the active repo design.
2. The current active system is still leaf-only and excerpt-only at the live contract level.
3. The **primary insertion boundary** for any future implementation is the excerpting Phase 2b → Phase 3/output boundary, where semantic granularity is chosen before it is flattened into `ExcerptRecord`.
4. Taxonomy is the **secondary required subsystem change** because it currently only places already-flat excerpts at leaves.
5. Synthesis would become a downstream consumer change after excerpting and taxonomy are widened.

Reason for the boundary conclusion:

- taxonomy cannot recover higher/coarser semantic units after excerpting has already flattened one `TeachingUnit` into one `ExcerptRecord`
- therefore taxonomy-first is insufficient as the first move, even though taxonomy must still change later

## What must not be forgotten

When Claude Code returns as main authority, this idea should be treated as a **pinned strategic planning topic** even if the owner forgets to mention it explicitly.

The required future question is:

- can the autonomous system itself originate ideas of this caliber on its own?

Not just:

- should we implement this exact idea now?

The first planning task should benchmark the autonomous system against this example and determine what changes to prompting, task generation, coworker review, evaluation, and memory would let it reliably generate ideas of this level.

## Future planning checklist

Before any implementation plan is accepted, require explicit agreement on:

1. whether this remains a benchmark/example only, or has become an active implementation target
2. whether “higher-level retained content” means raw preserved structural units, generated digests, or both
3. whether the first contract change belongs at excerpting output, taxonomy placement, or both in sequence
4. how provenance, deduplication, and branch-vs-leaf content coexist without ambiguity
5. how success will be measured for autonomous ideation quality, not just implementation correctness
