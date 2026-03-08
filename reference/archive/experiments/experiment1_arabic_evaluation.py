"""
Experiment 1: Can LLMs accurately evaluate Arabic scholarly claims?

10 claims about Islamic scholarship — 5 correct, 5 deliberately wrong.
Sent to 4 models via OpenRouter. Measures accuracy and cross-model agreement.
"""

import json
import time
from openai import OpenAI

# Claims: each has Arabic context, a claim, and ground truth
CLAIMS = [
    # === CORRECT CLAIMS (5) ===
    {
        "id": "C1",
        "claim_ar": "كتاب المغني في الفقه ألفه ابن قدامة المقدسي الحنبلي المتوفى سنة ٦٢٠ هـ",
        "claim_en": "Al-Mughni in fiqh was authored by Ibn Qudamah al-Maqdisi al-Hanbali (d. 620 AH)",
        "truth": "CORRECT",
        "why": "Ibn Qudamah (d. 620 AH) is indeed the author of al-Mughni, and he was Hanbali"
    },
    {
        "id": "C2", 
        "claim_ar": "ألفية ابن مالك نظم في علم النحو والصرف، نظمها محمد بن عبد الله بن مالك الطائي الجياني المتوفى سنة ٦٧٢ هـ",
        "claim_en": "Alfiyyat Ibn Malik is a versified text in nahw and sarf by Ibn Malik al-Ta'i (d. 672 AH)",
        "truth": "CORRECT",
        "why": "Ibn Malik (d. 672 AH) authored the Alfiyyah, a poem on Arabic grammar"
    },
    {
        "id": "C3",
        "claim_ar": "المذهب الحنفي ينسب إلى الإمام أبي حنيفة النعمان بن ثابت المتوفى سنة ١٥٠ هـ",
        "claim_en": "The Hanafi school is attributed to Imam Abu Hanifah al-Nu'man ibn Thabit (d. 150 AH)",
        "truth": "CORRECT",
        "why": "Abu Hanifah (d. 150 AH) is the founder of the Hanafi school"
    },
    {
        "id": "C4",
        "claim_ar": "صحيح البخاري يعتبر أصح كتاب بعد كتاب الله عند أهل السنة والجماعة",
        "claim_en": "Sahih al-Bukhari is considered the most authentic book after the Quran by Ahl al-Sunnah",
        "truth": "CORRECT",
        "why": "This is the standard Sunni scholarly consensus about Sahih al-Bukhari"
    },
    {
        "id": "C5",
        "claim_ar": "الإمام النووي شافعي المذهب، وكتابه المنهاج شرح صحيح مسلم بن الحجاج",
        "claim_en": "Imam al-Nawawi was Shafi'i, and his al-Minhaj is a commentary on Sahih Muslim",
        "truth": "CORRECT",
        "why": "Al-Nawawi was Shafi'i, and al-Minhaj is indeed his sharh of Sahih Muslim"
    },
    
    # === WRONG CLAIMS (5) ===
    {
        "id": "W1",
        "claim_ar": "كتاب الأم في الفقه ألفه الإمام مالك بن أنس",
        "claim_en": "Kitab al-Umm in fiqh was authored by Imam Malik ibn Anas",
        "truth": "WRONG",
        "why": "Al-Umm was authored by Imam al-Shafi'i, not Imam Malik. Malik authored al-Muwatta."
    },
    {
        "id": "W2",
        "claim_ar": "ابن تيمية كان شافعي المذهب وتوفي سنة ٧٢٨ هـ",
        "claim_en": "Ibn Taymiyyah was Shafi'i and died in 728 AH",
        "truth": "WRONG",
        "why": "Ibn Taymiyyah was Hanbali, not Shafi'i. Death date 728 AH is correct."
    },
    {
        "id": "W3",
        "claim_ar": "الورقات في أصول الفقه ألفها الإمام الغزالي أبو حامد",
        "claim_en": "Al-Waraqat in usul al-fiqh was authored by Imam al-Ghazali",
        "truth": "WRONG",
        "why": "Al-Waraqat was authored by Imam al-Juwayni (al-Haramayn), not al-Ghazali. Al-Ghazali was al-Juwayni's student."
    },
    {
        "id": "W4",
        "claim_ar": "زاد المعاد في هدي خير العباد كتاب في الحديث ألفه ابن حجر العسقلاني",
        "claim_en": "Zad al-Ma'ad is a hadith book by Ibn Hajar al-Asqalani",
        "truth": "WRONG",
        "why": "Zad al-Ma'ad was authored by Ibn al-Qayyim, not Ibn Hajar. It's also primarily a seerah/fiqh book, not a hadith collection."
    },
    {
        "id": "W5",
        "claim_ar": "المبتدأ في النحو العربي يكون منصوباً دائماً",
        "claim_en": "The mubtada' in Arabic grammar is always in the accusative case (mansub)",
        "truth": "WRONG",
        "why": "The mubtada' is marfu' (nominative), not mansub (accusative). This is a basic nahw rule."
    },
]

EVAL_PROMPT = """أنت محكّم متخصص في العلوم الإسلامية والعربية. سأعرض عليك ادعاءً علمياً وأريدك أن تحكم عليه.

الادعاء:
{claim_ar}

هل هذا الادعاء صحيح أم خاطئ؟

أجب بالتنسيق التالي فقط — لا تضف أي شيء آخر:
VERDICT: CORRECT أو WRONG
REASON: [سبب مختصر بالعربية أو الإنجليزية]
CONFIDENCE: HIGH أو MEDIUM أو LOW
"""

MODELS = [
    ("anthropic/claude-sonnet-4-20250514", "Claude Sonnet 4"),
    ("openai/gpt-4.1", "GPT-4.1"),
    ("google/gemini-2.5-flash", "Gemini 2.5 Flash"),
    ("deepseek/deepseek-chat", "DeepSeek V3"),
]


def run_experiment(api_key: str):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    results = []
    total_tokens = {"input": 0, "output": 0}
    
    for model_id, model_name in MODELS:
        print(f"\n{'='*60}")
        print(f"Testing: {model_name} ({model_id})")
        print(f"{'='*60}")
        
        model_correct = 0
        model_total = 0
        
        for claim in CLAIMS:
            prompt = EVAL_PROMPT.format(claim_ar=claim["claim_ar"])
            
            try:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    max_tokens=300,
                )
                
                answer = response.choices[0].message.content.strip()
                
                # Track tokens
                if response.usage:
                    total_tokens["input"] += response.usage.prompt_tokens
                    total_tokens["output"] += response.usage.completion_tokens
                
                # Parse verdict
                verdict = "UNKNOWN"
                if "CORRECT" in answer.upper().split('\n')[0]:
                    verdict = "CORRECT"
                elif "WRONG" in answer.upper().split('\n')[0]:
                    verdict = "WRONG"
                
                is_right = (verdict == claim["truth"])
                model_correct += int(is_right)
                model_total += 1
                
                status = "✓" if is_right else "✗"
                print(f"  {status} [{claim['id']}] Model: {verdict} | Truth: {claim['truth']}")
                if not is_right:
                    print(f"    Expected: {claim['why']}")
                    print(f"    Model said: {answer[:200]}")
                
                results.append({
                    "model": model_name,
                    "claim_id": claim["id"],
                    "truth": claim["truth"],
                    "verdict": verdict,
                    "correct": is_right,
                    "raw_answer": answer,
                })
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"  ERROR [{claim['id']}]: {e}")
                results.append({
                    "model": model_name,
                    "claim_id": claim["id"],
                    "truth": claim["truth"],
                    "verdict": "ERROR",
                    "correct": False,
                    "raw_answer": str(e),
                })
        
        accuracy = model_correct / model_total * 100 if model_total > 0 else 0
        print(f"\n  {model_name} accuracy: {model_correct}/{model_total} ({accuracy:.0f}%)")
    
    # Summary
    print(f"\n{'='*60}")
    print("EXPERIMENT 1 SUMMARY")
    print(f"{'='*60}")
    
    for model_id, model_name in MODELS:
        model_results = [r for r in results if r["model"] == model_name]
        correct = sum(1 for r in model_results if r["correct"])
        total = len(model_results)
        accuracy = correct / total * 100 if total > 0 else 0
        print(f"  {model_name}: {correct}/{total} ({accuracy:.0f}%)")
    
    # Cross-model agreement
    print(f"\nCross-model agreement:")
    for claim in CLAIMS:
        verdicts = {}
        for r in results:
            if r["claim_id"] == claim["id"]:
                verdicts[r["model"]] = r["verdict"]
        unique = set(verdicts.values()) - {"ERROR", "UNKNOWN"}
        agreement = "UNANIMOUS" if len(unique) <= 1 else f"SPLIT: {verdicts}"
        truth_match = all(v == claim["truth"] for v in verdicts.values() if v not in ("ERROR", "UNKNOWN"))
        symbol = "✓" if truth_match else "✗"
        print(f"  {symbol} [{claim['id']}] {agreement}")
    
    # Token usage
    print(f"\nTotal tokens: {total_tokens['input']} input + {total_tokens['output']} output")
    print(f"Arabic tokens per claim (avg): {total_tokens['input'] / (len(CLAIMS) * len(MODELS)):.0f} input")
    
    # Save results
    with open("/home/claude/experiment1_results.json", "w") as f:
        json.dump({"results": results, "tokens": total_tokens}, f, indent=2, ensure_ascii=False)
    
    return results, total_tokens


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python experiment1.py <OPENROUTER_API_KEY>")
        sys.exit(1)
    run_experiment(sys.argv[1])
