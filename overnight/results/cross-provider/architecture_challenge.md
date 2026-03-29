YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
This is a sophisticated architecture for a high-value niche. However, as a senior architect looking at a solo-developer project, I see several "brittle points" where the desire for academic rigor (consensus) collides with the reality of production engineering.

Here is my critical assessment:

### 1. The Weakest Assumption: CLI-Based Orchestration
The assumption that **CLI-based LLM calls** will scale or remain stable is your biggest risk. 
*   **The Breakpoint:** Subscription-based CLIs (like the one we are in) are designed for interactive use, not high-throughput piping. You will hit rate limits, hidden "safety" throttles, or local shell buffer overflows. 
*   **The Content Risk:** Arabic diacritics (Tashkeel) are notorious for being mangled by shell encodings (UTF-8 vs. ASCII vs. Windows-1256 from Shamela). Relying on a CLI to pass raw Arabic bytes back and forth between five engines will eventually lead to "mojibake" or lost diacritics despite your "frozen source" principle.

### 2. Over-Engineered: Multi-Model Consensus for *All* Decisions
Using Claude + GPT-5.4 for every minor classification is a "Gold-Plated" approach that adds exponential latency and complexity.
*   **The Fix:** Use a **Tiered Logic** approach. 
    *   Simple classification/normalization: Use a local, fast model (like a fine-tuned Llama-3-8B or even traditional NLP like CAMeL Tools). 
    *   The "Council" (Consensus): Only invoke this when the local model’s confidence score is low or for the "Excerpting" phase which is your "Teaching Unit" core.

### 3. What I would do COMPLETELY differently: Vector-First Taxonomy
Instead of asking an LLM "Where does this fit in the tree?" for every excerpt:
1.  **Embed the Taxonomy:** Convert your science trees (Usul, Fiqh, Hadith) into a dense vector space of "Definitions."
2.  **Semantic Mapping:** Use a local embedding model (like `bge-m3` which is excellent for Arabic) to find the nearest neighbor in the taxonomy.
3.  **LLM as Judge:** Only use the LLM to verify the top 3 semantic matches. This turns a *generative* problem into a *ranking* problem, which is 10x cheaper and more accurate.

### 4. Arabic NLP Alternatives
You are currently treating Arabic as a "black box" for LLMs. You should integrate:
*   **CAMeL Tools (NYU Abu Dhabi):** The gold standard for Arabic morphological analysis, lemmatization, and de-diacritization.
*   **AraBERT / QARiB:** For your Taxonomy engine, a BERT-based model trained on Classical Arabic will outperform a general-purpose GPT-5.4 at "understanding" the difference between *Maliki* and *Shafi'i* nuance in a 13th-century text.
*   **Shamela-specific parsers:** Instead of custom HTML extraction, look at `shamela-scraper` or existing community tools that handle the weirdness of Shamela’s specific `BOK` format versions.

### 5. Unlimited Budget Addition: Human-in-the-Loop (HITL) Gold Dataset
If money were no object, I wouldn't buy more tokens; I would hire **3-5 Azhari scholars** to manually label 10,000 excerpts. 
*   **Why?** LLMs are "hallucination-prone" regarding specific Islamic legal rulings. A "Gold Dataset" allows you to fine-tune a local model (e.g., "Misk-70B") that actually understands the *Isnad* (chain of narration) logic better than a general-purpose American LLM.

### 6. The "3-Engine" Cut
If you have to streamline, remove **Normalization** and **Synthesis**.

*   **Remove Normalization:** Merge this into the **Source** engine. Text cleaning should be a byproduct of extraction, not a standalone microservice with its own Pydantic overhead.
*   **Remove Synthesis:** Synthesis is usually a "View" concern. If your **Taxonomy** and **Excerpting** are high-quality, "Synthesis" is just a Jinja2 template or a JSON export. It doesn't need to be an "Engine."

**Keep these three:**
1.  **Source:** (Because garbage in = garbage out).
2.  **Excerpting:** (This is your unique value proposition—the "Teaching Units").
3.  **Taxonomy:** (This is how users find the content).

### Final Architectural "Pro-Tip":
Check your **D-023 rule** (metadata preservation). In Arabic scholarly texts, the `page/volume` and `chapter head` metadata are often more important than the text itself for citation. Ensure your `contracts.py` treats `ancestor_headers` as a first-class array, not just a string blob.
