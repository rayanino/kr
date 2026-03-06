# Silent Failure Patterns — أنماط الفشل الصامت

These are specific patterns where Claude produces output that LOOKS correct but is subtly wrong. Each pattern includes detection criteria and concrete examples from KR's domain.

The danger: a SPEC section that reads fluently, passes a cursory review, and would be approved by a non-expert — but that would produce wrong behavior when implemented.

---

## Pattern 1: The Hollow Example

**What it looks like:** An example is present. It has input and output. It uses Arabic text. It looks complete.

**What's wrong:** The example doesn't actually test the rule it claims to illustrate. It shows the happy path but the rule is about edge cases.

**Detection test:** For each example, ask: "If I implemented the rule WRONG, would this example still pass?" If yes, the example is hollow.

**Concrete KR example:**
```
BAD: "Example: Given a source titled 'شرح ابن عقيل', the engine extracts the title."
→ This tests nothing. ANY implementation extracts a title from a field labeled "title."

GOOD: "Example: Given a source titled 'شرح ابن عقيل على ألفية ابن مالك', the engine:
(1) extracts the full title
(2) detects this is a sharh (شرح = commentary)  
(3) identifies the base work (ألفية ابن مالك)
(4) identifies two scholars: ابن عقيل (commentator) and ابن مالك (original author)
(5) creates a work relationship: sharh → base_work"
→ This tests multi-layer detection, a real edge case.
```

---

## Pattern 2: The Circular Definition

**What it looks like:** A rule defines behavior using terms that sound precise but ultimately reference themselves.

**What's wrong:** An implementer reads the rule, nods, and has no idea what to actually build.

**Detection test:** Replace every defined term with its definition. Does the resulting sentence still have content? Or is it "X is done by doing X"?

**Concrete KR example:**
```
BAD: "The engine evaluates relevance using content analysis."
→ What IS content analysis? This says "evaluates relevance by evaluating relevance."

GOOD: "The engine evaluates relevance by: (1) extracting the first 2000 characters or table of contents,
(2) sending it to the LLM with the library's science inventory, 
(3) classifying the match as relevant/partially_relevant/not_relevant based on whether 
    the source's topics overlap with any registered science."
→ Three concrete steps. An implementer knows exactly what to build.
```

---

## Pattern 3: The Hand-Waving Technology Reference

**What it looks like:** A capability names a technology or approach. It sounds feasible.

**What's wrong:** The named technology doesn't actually do what the SPEC claims, or it doesn't work for Arabic, or it requires setup the SPEC doesn't mention.

**Detection test:** Search for the named technology. Read the actual documentation. Does it support Arabic? Does it support the specific use case?

**Concrete KR example:**
```
BAD: "Use sentence-transformers for Arabic semantic search."
→ Most sentence-transformers models don't handle Arabic well. The default 
   all-MiniLM-L6-v2 has poor Arabic performance.

GOOD: "Use arabic-e5-base or GTE-multilingual-base for Arabic semantic search.
These models are specifically trained on Arabic text and achieve >0.75 NDCG 
on Arabic retrieval benchmarks. See RESOURCES.md for evaluation details."
→ Specific model names with evidence of Arabic support.
```

---

## Pattern 4: The Phantom Metadata

**What it looks like:** The SPEC says "field X is passed through from upstream." The downstream SPEC says "field X is consumed."

**What's wrong:** The field is named differently at each boundary, or it has a different type, or the upstream engine doesn't actually produce it.

**Detection test:** Run `python3 scripts/verify_metadata_flow.py --boundary upstream downstream`. Also manually check: are the field NAMES identical? Are the TYPES identical? Is the field OPTIONAL in one place and REQUIRED in another?

**Concrete KR example:**
```
BAD: Source SPEC says output has "school_attribution". Normalization SPEC expects "madhhab". 
     Both mean the same thing but the names don't match.

GOOD: Both SPECs use "school_attribution" consistently. The field type is 
     { school: string, confidence: float, source: "extracted" | "inferred" | "unknown" }
     at both boundaries.
```

---

## Pattern 5: The Untestable Rule

**What it looks like:** A rule uses subjective language that seems precise.

**What's wrong:** Two different implementers would produce different behavior. There's no objective test.

**Detection test:** Can you write a test case with a clear pass/fail criterion? If the criterion requires human judgment, the rule is untestable.

**Concrete KR example:**
```
BAD: "The engine extracts excerpts that are scholarly valuable."
→ What IS "scholarly valuable"? Two LLMs would disagree.

GOOD: "The engine extracts excerpts that: (1) contain at least one explicit scholarly position 
(marked by opinion verbs: يرى, يقول, الراجح, etc.), (2) are attributable to a named 
or identifiable author/school, (3) pass self-containment check (understandable without 
surrounding context)."
→ Three checkable criteria. A test can verify each one.
```

---

## Pattern 6: The Missing Error Path

**What it looks like:** The SPEC describes what happens when everything goes right. Processing is described step by step.

**What's wrong:** When something goes wrong (and it will), the implementer doesn't know what to do. The engine silently drops data or crashes.

**Detection test:** For each processing step, ask: "What happens if this step fails?" If the answer isn't in the SPEC, it's a missing error path.

**Concrete KR example:**
```
BAD: "The engine sends the text to the LLM for classification."
→ What if the LLM returns an error? Times out? Returns garbage? 
   Returns a classification not in the expected set?

GOOD: "The engine sends the text to the LLM for classification.
If the LLM call fails (timeout, error, or invalid response):
- First retry: same model, fresh request.
- Second retry: fallback model.  
- Both retries failed: log error SRC_LLM_FAILURE, create human gate checkpoint 
  with the source_id and step that failed, mark source as needs_manual_classification."
→ Every failure mode has a defined response.
```

---

## Pattern 7: The Scope Creep Disguise

**What it looks like:** A §4.B capability sounds transformative. It's well-written and exciting.

**What's wrong:** It's actually describing something another engine does, or something the scholar interface does, or something that requires capabilities this engine doesn't have.

**Detection test:** Could this capability be implemented using ONLY this engine's input and the tools this engine has access to? Or does it require calling other engines?

**Concrete KR example:**
```
BAD (in source engine §4.B): "The engine generates a book briefing summarizing 
the source's content, organization, and scholarly significance."
→ This requires reading the CONTENT, which is the normalization engine's job.
   The source engine only sees metadata, not full text.

GOOD (in source engine §4.B): "The engine generates a source intelligence report 
from metadata alone: estimated significance based on citation count in OpenITI, 
author's position in the teacher-student graph, genre rarity in the library,
and tahqiq quality indicators."
→ Uses only data the source engine actually has.
```

---

## How to Use This Document

During SPEC refinement (Step 1: Cold Read and Step 7: Self-Review):
1. Read each §4 rule through the lens of these 7 patterns.
2. For each pattern: "Does this rule exhibit this failure pattern?"
3. Flag matches as defects in the defect ledger.
4. Fix them in Step 7.

This document is a DETECTION tool, not a process. It doesn't add steps to the refinement cycle — it sharpens the eyes you use during existing steps.
