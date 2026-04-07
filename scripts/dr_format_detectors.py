"""Auto-detect DR response provider and extract provider-specific structure.

Each DR provider (ChatGPT, Claude, Gemini) produces distinct markdown patterns.
This module detects the provider and extracts sections using provider-aware strategies.

Reference: docs/autonomous-system/reviews/ (8 archived DRs with observed patterns)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from scripts.autonomous_schemas import DRTarget


@dataclass
class DetectionResult:
    """Result of provider auto-detection."""

    provider: DRTarget
    confidence: float  # 0.0-1.0
    signals: list[str] = field(default_factory=list)


def detect_provider(text: str) -> DetectionResult:
    """Auto-detect DR provider from content markers.

    Observed patterns from 8 archived DRs (DR32-DR39):
    - ChatGPT: fileciteturn citations, scored tables, no embedded Arabic
    - Claude: numbered headings (## 1.), code blocks, academic structure
    - Gemini: footnote superscripts, full embedded Arabic with diacritics
    """
    scores: dict[DRTarget, float] = {
        DRTarget.CHATGPT: 0.0,
        DRTarget.CLAUDE: 0.0,
        DRTarget.GEMINI: 0.0,
    }
    signals: dict[DRTarget, list[str]] = {t: [] for t in DRTarget}

    # ChatGPT signals — \ue202 private-use chars appear between tokens in ChatGPT DR output
    filecite_count = len(re.findall(r"filecite[\ue200-\ue2ff]*turn[0-9]+file[0-9]+", text))
    if filecite_count > 0:
        scores[DRTarget.CHATGPT] += 0.6
        signals[DRTarget.CHATGPT].append(f"fileciteturn citations: {filecite_count}")

    if re.search(r"\|\s*Candidate\s*\|.*Weighted total\s*\|", text):
        scores[DRTarget.CHATGPT] += 0.2
        signals[DRTarget.CHATGPT].append("scored comparison table")

    # Claude signals
    numbered_headings = len(re.findall(r"^##\s+[0-9]+\.", text, re.MULTILINE))
    if numbered_headings >= 2:
        scores[DRTarget.CLAUDE] += 0.4
        signals[DRTarget.CLAUDE].append(f"numbered headings: {numbered_headings}")

    code_blocks = len(re.findall(r"```python", text))
    if code_blocks > 0:
        scores[DRTarget.CLAUDE] += 0.2
        signals[DRTarget.CLAUDE].append(f"python code blocks: {code_blocks}")

    if re.search(r"### [A-Z]\.", text):
        scores[DRTarget.CLAUDE] += 0.2
        signals[DRTarget.CLAUDE].append("lettered sub-headings")

    # Gemini signals — embedded Arabic with diacritics (tashkeel)
    arabic_with_diacritics = len(re.findall(
        r"[\u0600-\u06FF][\u0610-\u065F]", text
    ))
    if arabic_with_diacritics > 5:
        scores[DRTarget.GEMINI] += 0.4
        signals[DRTarget.GEMINI].append(f"Arabic with diacritics: {arabic_with_diacritics}")

    # Gemini dual-language headings: ### N. English / Arabic
    dual_headings = len(re.findall(
        r"^###\s+[0-9]+\.\s+.+[\u0600-\u06FF]", text, re.MULTILINE
    ))
    if dual_headings > 0:
        scores[DRTarget.GEMINI] += 0.3
        signals[DRTarget.GEMINI].append(f"dual-language headings: {dual_headings}")

    # Gemini footnote-style superscripts (digit after sentence, not in brackets)
    footnotes = len(re.findall(r"[.!?][0-9]{1,2}\s", text))
    if footnotes >= 3:
        scores[DRTarget.GEMINI] += 0.2
        signals[DRTarget.GEMINI].append(f"footnote superscripts: {footnotes}")

    # Pick highest score
    best = max(scores, key=lambda t: scores[t])
    return DetectionResult(
        provider=best,
        confidence=min(scores[best], 1.0),
        signals=signals[best],
    )


# ═══════════════════════════════════════════════════════════════════
# Section extraction — provider-aware
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Section:
    """A section extracted from a DR response."""

    heading: str
    body: str
    level: int  # heading level (2 for ##, 3 for ###, etc.)


def extract_sections(text: str, provider: DRTarget) -> list[Section]:
    """Extract sections using provider-aware heading detection."""
    # Strip ChatGPT fileciteturn noise before parsing
    if provider == DRTarget.CHATGPT:
        text = re.sub(r"\s*filecite[\ue200-\ue2ff]*turn[0-9]+file[\ue200-\ue2ff]*[0-9]+[\ue200-\ue2ff]*L[0-9]+-L[0-9]+[\ue200-\ue2ff]*", "", text)

    sections: list[Section] = []
    current_heading = ""
    current_level = 0
    current_body: list[str] = []

    for line in text.split("\n"):
        heading_match = re.match(r"^(#{2,4})\s+(.+)", line)
        if heading_match:
            if current_heading or current_body:
                sections.append(Section(
                    heading=current_heading,
                    body="\n".join(current_body).strip(),
                    level=current_level,
                ))
            current_level = len(heading_match.group(1))
            current_heading = heading_match.group(2).strip()
            current_body = []
        else:
            current_body.append(line)

    if current_heading or current_body:
        sections.append(Section(
            heading=current_heading,
            body="\n".join(current_body).strip(),
            level=current_level,
        ))

    return sections


# ═══════════════════════════════════════════════════════════════════
# Paragraph extraction with role classification
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Paragraph:
    """A classified paragraph from a DR section."""

    text: str
    role: str  # recommendation, analysis, evidence, question, metadata
    confidence: float


_RECOMMENDATION_KW = [
    "should", "must", "recommend", "implement", "change",
    "add", "remove", "fix", "update", "create", "replace",
    "needs to", "required", "ensure", "the engine must",
    "the system should", "the pipeline must",
]

_QUESTION_KW = ["?", "\u061F", "unclear whether", "further research", "unknown"]

_EVIDENCE_KW = [
    "for example", "e.g.", "such as", "specifically",
    "cite", "according to", "in the text", "the hadith",
]


def classify_paragraphs(body: str) -> list[Paragraph]:
    """Split section body into paragraphs and classify each by role."""
    # Split on double newlines (paragraph breaks) or list item boundaries
    raw_paragraphs = re.split(r"\n\s*\n", body)
    result: list[Paragraph] = []

    for raw in raw_paragraphs:
        text = raw.strip()
        if not text or len(text) < 15:
            continue

        lower = text.lower()

        # Score each role
        rec_score = sum(1 for kw in _RECOMMENDATION_KW if kw in lower)
        q_score = sum(1 for kw in _QUESTION_KW if kw in text)  # case-sensitive for ?
        ev_score = sum(1 for kw in _EVIDENCE_KW if kw in lower)

        if rec_score >= 2:
            role = "recommendation"
            confidence = min(0.5 + rec_score * 0.1, 1.0)
        elif q_score >= 1:
            role = "question"
            confidence = min(0.5 + q_score * 0.15, 1.0)
        elif ev_score >= 2:
            role = "evidence"
            confidence = min(0.4 + ev_score * 0.1, 0.9)
        else:
            role = "analysis"
            confidence = 0.5

        result.append(Paragraph(text=text, role=role, confidence=confidence))

    return result


# ═══════════════════════════════════════════════════════════════════
# Content extraction — spec_sections, affected_files
# ═══════════════════════════════════════════════════════════════════

_SPEC_SECTION_RE = re.compile(
    r"(?:§|SPEC\s+§?|section\s+)([0-9]+(?:\.[0-9A-Za-z]+)*)",
    re.IGNORECASE,
)

_ENGINE_NAMES = [
    "excerpting", "taxonomy", "passaging", "atomization",
    "normalization", "source", "synthesis",
]

_FILE_PATH_RE = re.compile(
    r"(?:[\w\-]+/)+[\w\-]+\.(?:py|md|yaml|json|jsonl|html|txt)"
)


def extract_spec_sections(text: str) -> list[str]:
    """Extract SPEC section references from text."""
    refs: set[str] = set()
    for m in _SPEC_SECTION_RE.finditer(text):
        refs.add(f"§{m.group(1)}")
    # Also detect engine names as implicit section refs
    lower = text.lower()
    for engine in _ENGINE_NAMES:
        if engine in lower:
            refs.add(engine)
    return sorted(refs)


def extract_affected_files(text: str) -> list[str]:
    """Extract file path references from text."""
    return sorted(set(_FILE_PATH_RE.findall(text)))
