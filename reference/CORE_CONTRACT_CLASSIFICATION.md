# Core Contract Classification — تصنيف العقود الأساسية

**Purpose:** Identifies which Pydantic models in each engine's contracts.py are CORE (needed for the tracer bullet and Stage 1 pipeline) vs. DEFERRED (§4.B features, advanced capabilities, extra formats). The tracer bullet reconciles only CORE models across boundaries.

**Date:** 2026-03-09
**Criteria:** A model is CORE if the minimal pipeline (Shamela HTML → knowledge entry) cannot produce meaningful output without it. Everything else is DEFERRED.

---

## Source Engine (contracts.py — 825 lines, 45 classes)

### CORE (27 classes)
**Enums:** SourceFormat¹, OwnerAuthoredType, TrustTier, TextFidelity, AuthorityLevel, StructuralFormat, Genre, GenreRelationType, WorkLevel, ProcessingStatus, AcquisitionPath, ErrorSeverity, ErrorCode, HumanGateTrigger

**Models:** ScholarReference, TextLayer, GenreChain, WorkRelationshipEdge, TrustworthinessFactor, MetadataHistoryEntry, VolumeInfo, InferredFieldConfidence, ScholarAuthorityRecord, WorkRegistryEntry, SourceRegistryEntry, SourceMetadata, SourceError

¹ SourceFormat enum has 8 values; only `shamela_html` and `plain_text` are exercised in Stage 1.

### DEFERRED (18 classes — §4.B features)
**Citation network:** CitationDiscoveryRequest, RelevanceEvaluation, GapAnalysisItem
**Cross-validated scholar bootstrapping:** DeathDateAgreement, KnownWorksUnion, WikidataTeacherStudentLinks, CrossValidationDiscrepancy, CrossValidationResult, GenealogyMetadata
**Source difficulty prediction:** TextReuseEntry, IntertextualMetrics, CompositionalProfile, DifficultySignal, DifficultyPrediction
**Edition comparison:** EditionDivergence, EditionComparisonSummary, EditionComparison
**Tahqiq fingerprinting:** TahqiqFingerprint

### BOUNDARY NOTE
EnrichmentRequest, HumanGateCheckpoint, RegistryPendingWrite are operational models (not in the output contract). Include in tracer bullet for completeness but they don't affect the source→normalization boundary.

---

## Normalization Engine (contracts.py — 53 classes)

### CORE (22 classes)
**Enums:** TextFidelityLevel, LayerType, HeadingConfidence, HeadingDetectionMethod, FootnoteType, StructuralFormat

**Models:** PhysicalPage, TextLayerSegment, Footnote, StructuralMarkers, ContentFlags, TextFidelity, ContentUnit, DivisionNode, LayerMapEntry, TextFidelitySummary, QualityReport, ContentCensus, NormalizedManifest, NormalizedPackage

**Why LayerType is CORE:** Basic matn/sharh/hashiyah detection using CSS classes is core per ENGINE_PROTOCOL. Without it, downstream engines cannot attribute text to the correct author.

### DEFERRED (31 classes)
**Verse handling:** VerseLineHemistich, VerseLine, VerseInfo (verse format deferred to Stage 2)
**Advanced footnote types:** VariantReadingData, TakhrijData, BiographicalNoteData, CorrectionNoteData, SecondaryFootnoteType
**Discourse analysis:** DiscourseSegmentType, DominantDiscourseType, DiscourseDetectionMethod, DiscourseSegment, DiscourseFlow, BoundaryContinuityType, ContinuityDetectionMethod, BoundaryContinuity
**Layer fingerprinting:** SentenceLengthStats, FingerprintReliability, LayerFingerprint
**Advanced census:** TextDensityProfile, LayerComplexity, StructuralDepth, FootnoteDensity, VocabularyProfile, FidelityDistribution
**Tahqiq topology:** ManuscriptWitness, DivisionDisagreement, EditionReliability, TahqiqTopology

---

## Passaging Engine (contracts.py — 34 classes)

### CORE (18 classes)
**Enums:** ReviewFlag, HeadingSource, PassageStructuralFormat², SizingAction, ErrorSeverity, PassagingErrorCode

**Models:** PassageTextLayerSegment, PassageFootnote, DivisionPathEntry, UnitRange, PhysicalPages, PassageContentFlags, PassageTextFidelity, PassageSizing, PassageRecord, PassageStream, PassagingConfig

² PassageStructuralFormat: only `prose` and `commentary` values exercised in Stage 1. `verse` and `dictionary` are deferred.

### DEFERRED (16 classes)
**Verse handling:** PassageVerseLineInfo, PassageVerseInfo
**Advanced commentary alignment:** MatnSegment, CommentarySpan, CommentaryAlignmentRecord, CommentarySensitivity
**Quality prediction:** QualityPrediction
**Argument detection:** ArgumentCompleteness, ArgumentDetectionSource, ArgumentStructure, DanglingDiscourse, AdaptiveParams
**Completeness forecast:** CompletenessLevel, CompletenessForecast
**Cross-edition:** CrossEditionCorrespondence, CrossEditionMap

---

## Atomization Engine (contracts.py — 35 classes)

### CORE (20 classes)
**Enums:** StructuralType, ScholarlyFunction, SourceLayer, EmbeddedRefType, DetectionMethod, AtomRelationType, AttributionType, ReviewFlag, ErrorSeverity, AtomizationErrorCode

**Models:** AnchorSpan, QuranRefDetail, HadithRefDetail, EmbeddedRef, FootnoteRef, AtomRelation, ScholarlyAttribution, AtomRecord, AtomStream, AtomizationConfig

### DEFERRED (15 classes)
**Evidence quality:** EvidenceQualitySignalType, QualityDirection, EvidenceQualitySignal, ArgumentCompletenessScore
**Advanced refs:** PoetryRefDetail, ScholarlyQuoteRefDetail
**Concordance/fingerprinting:** ConcordanceEntry, PassageTypeDistribution, SourceTypeDistribution, FingerprintManifestEntry, FingerprintManifest
**Term index:** TermIndexEntry, TermIndex

---

## Excerpting Engine (contracts.py — 40 classes)

### CORE (12 classes)
**Enums:** LifecycleStage, ContextAtomRole, ExcerptKind

**Models:** ContextAtom, QuotedScholar, EvidenceRef, PhysicalPages, ProcessingMetadata, ExcerptRecord, ExcerptStream

**Note:** The excerpting engine's core is the narrowest — extract self-contained excerpts from atom streams. Most of the 40 classes are §4.B advanced analysis features.

### DEFERRED (28 classes)
**Argument mapping:** ArgumentRole, ArgumentMapSegment, ArgumentCompleteness, LogicalStructure, IslamicArgumentType
**Dialogue detection:** DialogueType, DialogueLink
**Semantic dedup:** SemanticDuplicateRelation, SemanticDuplicateLink
**Masala analysis:** MasalaExcerptType, MasalaScope, MasalaAnalysis
**Evidence chains:** EvidenceType, EvidenceLinkType, EvidenceChainClaim, EvidenceLink, EvidenceChain
**Resonance detection:** ResonanceTier, ResonanceType, ChronologicalDirection, ResonanceLink
**Repair:** RepairSuggestionType, RepairSuggestion
**Advanced refs:** QuotedScholarRole, QuranDetail, HadithDetail, TakhrijEntry, TerminologyVariant, VerseNumbers

---

## Taxonomy Engine (contracts.py — 43 classes)

### CORE (10 classes)
**Enums:** TreeNodeType, HumanGateType, HumanGateDecision, GapType

**Models:** TreeNode, PlacedExcerptAdditions, HumanGateDecisionRecord, CoverageGap, LeafCoverage

**Note:** Taxonomy core is: receive a science tree, place excerpts into leaves, detect gaps. Everything else is §4.B.

### DEFERRED (33 classes)
**Placement review:** PlacementReviewOutcome, VerifiedFlaggedStatus, PlacementReviewMetadata, ExcerptRelocationRequest
**Prerequisites:** PrerequisiteStrength, PrerequisiteEdge
**Cross-science:** CrossScienceLinkType, CrossScienceLink
**Terminology:** TerminologySynonym, TermVariant
**Evolution:** EvolutionChangeType, EvolutionPredictionType, EvolutionInvariantChecks, EvolutionProposal, ExcerptRedistribution
**Disagreement topology:** DisagreementCategory, DisagreementPosition, IntraSchoolDisagreement, LeafDisagreementClassification, DominantDisagreementAxis, DisagreementTopology
**Scholarly landscape:** DiscourseTransitionType, InfluenceType, ScholarNode, InfluenceEdge, ChronologicalPosition, DiscourseTransition, EvidenceEvolutionPeriod, SchoolPositioningSummary, ScholarlyLandscape
**Predictions:** SplitPrediction, GapPrediction, SourceEvolutionPredictions, TemporalSpan

---

## Synthesis Engine (contracts.py — 46 classes)

### CORE (16 classes)
**Enums:** GroundingType, ClaimType, TargetSection

**Models:** PositionHolder, ScholarlyPosition, ScholarlyAnalysis, PlannedClaim, ClaimAttribution, ExcerptSpan, Citation, ScholarlyPositionEntry, EntryContent, GenerationMetadata, Entry, QualityAssessment

**Note:** Core synthesis is: receive excerpts, produce a structured entry with traceable claims, temporal ordering, and school attribution. The full scholarly narrative with intellectual genealogy and consensus shift analysis is aspirational for v0.0.1 but the data model must support it.

### DEFERRED (30 classes)
**Khilaf analysis:** KhilafClassificationType, ContradictionNature, ConsensusStrength, KhilafClassification, ContradictionCheckResult, IntraAuthorContradiction, AbrogationFlag, KhilafDisambiguationResult, DisagreementLocusType, DisagreementLocus
**Entailment verification:** AtomicSubClaimType, AtomicSubClaim, EntailmentResult
**Self-assessment:** AssessmentLevel, PositionRelationship, AssessmentQuestion, SelfVerificationResult, AssessmentSet
**Staleness/regeneration:** StalenessTriggertType, RegenerationPriority, StalenessSignal, RegenerationRequest
**Corrections:** CorrectionType, OwnerCorrection
**Versioning:** ChangeSummary, EntryVersionRecord
**Enrichment:** ConsensusMapping, GenealogyChain, GapType, GapNote

---

## Summary

| Engine | Total classes | Core | Deferred | Core % |
|--------|-------------|------|----------|--------|
| Source | 45 | 27 | 18 | 60% |
| Normalization | 53 | 22 | 31 | 42% |
| Passaging | 34 | 18 | 16 | 53% |
| Atomization | 35 | 20 | 15 | 57% |
| Excerpting | 40 | 12 | 28 | 30% |
| Taxonomy | 43 | 10 | 33 | 23% |
| Synthesis | 46 | 16 | 30 | 35% |
| **Total** | **296** | **125** | **171** | **42%** |

The tracer bullet reconciles 125 classes across 6 boundaries instead of 296. This is a 58% reduction in reconciliation scope.

---

## Boundary Reconciliation Priority

The tracer bullet must verify these specific boundary contracts:

1. **source → normalization:** SourceMetadata fields that NormalizedPackage references via source_id
2. **normalization → passaging:** NormalizedPackage (specifically ContentUnit, DivisionNode, LayerMapEntry) → PassageStream input expectations
3. **passaging → atomization:** PassageRecord fields → AtomRecord input expectations
4. **atomization → excerpting:** AtomRecord/AtomStream → ExcerptRecord assembly
5. **excerpting → taxonomy:** ExcerptRecord → PlacedExcerptAdditions mapping
6. **taxonomy → synthesis:** PlacedExcerptAdditions + ExcerptRecord → Entry assembly
