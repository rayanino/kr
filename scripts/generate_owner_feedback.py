"""Generate owner feedback HTML with fresh excerpts only."""
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    root = Path("integration_tests")

    # Load owner's prior feedback to know what NOT to re-show
    reviewed_ids: set[str] = set()
    fb_path = root / "campaign_20260331/taysir/owner_feedback.jsonl"
    if fb_path.exists():
        with open(fb_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    reviewed_ids.add(json.loads(line.strip())["excerpt_id"])

    # Load rerun excerpts, exclude reviewed
    excerpts: list[dict] = []
    with open(root / "campaign_rerun_20260408/excerpts.jsonl", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                e = json.loads(line.strip())
                if e["excerpt_id"] not in reviewed_ids:
                    excerpts.append(e)

    # Selection: 5 diverse excerpts from different divisions and PFs
    picks: list[tuple[str, dict]] = []
    used_ids: set[str] = set()
    used_divs: set[str] = set()

    def add(label: str, e: dict) -> None:
        picks.append((label, e))
        used_ids.add(e["excerpt_id"])
        used_divs.add(e["div_id"])

    # A: hadith from a deep chapter
    for e in excerpts:
        if e["div_id"] in used_divs or e["excerpt_id"] in used_ids:
            continue
        if "_6_" not in e["div_id"]:
            continue
        pf = e.get("primary_function", "")
        wc = len(e.get("primary_text", "").split())
        if pf == "evidence_hadith" and 80 <= wc <= 200 and e.get("self_containment") == "FULL":
            add("A", e)
            break

    # B: rule_statement with school from vol 7
    for e in excerpts:
        if e["div_id"] in used_divs or e["excerpt_id"] in used_ids:
            continue
        if "_7_" not in e["div_id"]:
            continue
        pf = e.get("primary_function", "")
        wc = len(e.get("primary_text", "").split())
        school = e.get("school", "")
        if pf == "rule_statement" and school and school not in ("not_applicable", "") and 60 <= wc <= 150:
            add("B", e)
            break

    # C: definition from salat
    for e in excerpts:
        if e["div_id"] in used_divs or e["excerpt_id"] in used_ids:
            continue
        if "_2_" not in e["div_id"]:
            continue
        pf = e.get("primary_function", "")
        wc = len(e.get("primary_text", "").split())
        if pf == "definition" and 30 <= wc <= 120 and e.get("self_containment") == "FULL":
            add("C", e)
            break

    # D: refutation
    for e in excerpts:
        if e["div_id"] in used_divs or e["excerpt_id"] in used_ids:
            continue
        pf = e.get("primary_function", "")
        wc = len(e.get("primary_text", "").split())
        if pf == "refutation" and 50 <= wc <= 200:
            add("D", e)
            break

    # E: opinion from middle of the book
    mid = len(excerpts) // 2
    for e in excerpts[mid:]:
        if e["div_id"] in used_divs or e["excerpt_id"] in used_ids:
            continue
        pf = e.get("primary_function", "")
        wc = len(e.get("primary_text", "").split())
        if pf == "opinion_statement" and 60 <= wc <= 200:
            add("E", e)
            break

    # Build HTML
    pf_ar = {
        "definition": "تعريف",
        "evidence_hadith": "دليل حديثي",
        "rule_statement": "حكم فقهي",
        "opinion_statement": "رأي علمي",
        "refutation": "مناقشة ورد",
    }

    parts = [
        '<!DOCTYPE html>\n<html lang="ar" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
        "<title>Owner Feedback - 5 Fresh Excerpts</title>\n<style>\n"
        "  body { font-family: 'Traditional Arabic','Amiri','Scheherazade New',serif;"
        " background:#1a1a2e; color:#e0e0e0; max-width:900px; margin:40px auto;"
        " padding:20px; line-height:2; font-size:20px; }\n"
        "  h1 { color:#e94560; text-align:center; font-size:28px; margin-bottom:10px; }\n"
        "  .sub { text-align:center; color:#999; font-size:16px; margin-bottom:40px;"
        " font-family:sans-serif; direction:ltr; }\n"
        "  .card { background:#16213e; border:1px solid #0f3460; border-radius:12px;"
        " padding:24px 30px; margin-bottom:30px; }\n"
        "  .lbl { color:#e94560; font-size:14px; font-family:sans-serif; direction:ltr;"
        " text-align:left; margin-bottom:8px; }\n"
        "  .meta { color:#888; font-size:13px; font-family:sans-serif; direction:ltr;"
        " text-align:left; margin-bottom:16px; border-bottom:1px solid #0f3460;"
        " padding-bottom:12px; }\n"
        "  .txt { font-size:22px; line-height:2.2; color:#f0f0f0; }\n"
        "  .topic { color:#53d8fb; font-size:16px; margin-top:12px; }\n"
        "  .fb { background:#0f3460; border-radius:8px; padding:16px 20px; margin-top:16px; }\n"
        "  .fb p { color:#aaa; font-size:14px; font-family:sans-serif; direction:ltr; margin:4px 0; }\n"
        "  .inst { background:#0f3460; border-radius:8px; padding:20px; margin-bottom:40px;"
        " font-family:sans-serif; direction:ltr; text-align:left; font-size:15px;"
        " color:#ccc; line-height:1.8; }\n"
        "  .inst strong { color:#e94560; }\n"
        "</style>\n</head>\n<body>\n"
        '<h1>5 مقتطفات جديدة للمراجعة</h1>\n'
        '<div class="sub">Campaign Rerun 2026-04-08 &mdash; Fresh excerpts only'
        " (none previously reviewed)</div>\n"
        '<div class="inst">\n'
        "  <strong>How to read these:</strong> Each card is one teaching unit from"
        " Taysir al-Allam. None overlap with your previous feedback. Read as if"
        " studying, then react honestly:\n"
        "  <ul>\n"
        "    <li>Does it make sense on its own?</li>\n"
        "    <li>Right amount of information?</li>\n"
        "    <li>Useful as a study note?</li>\n"
        '    <li>Any reaction at all</li>\n'
        "  </ul>\n</div>\n",
    ]

    for label, e in picks:
        text = e.get("primary_text", "")
        wc = len(text.split())
        pf = e.get("primary_function", "")
        sc = e.get("self_containment", "")
        topic = e.get("excerpt_topic", [])
        school = e.get("school", "")
        flags = e.get("review_flags", []) or []
        div_path = e.get("div_path", [])

        topic_str = " / ".join(topic) if isinstance(topic, list) else str(topic)
        path_str = " > ".join(div_path) if isinstance(div_path, list) else str(div_path)
        text_html = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )
        flag_str = ", ".join(flags) if flags else "none"

        parts.append(
            f'<div class="card">\n'
            f'  <div class="lbl">EXCERPT {label} &mdash; {pf} &bull; {wc} words'
            f" &bull; SC: {sc}</div>\n"
            f'  <div class="meta">Type: {pf_ar.get(pf, pf)} | School: {school or "N/A"}'
            f" | Path: {path_str}<br>"
            f"Flags: {flag_str}</div>\n"
            f'  <div class="txt">{text_html}</div>\n'
            f'  <div class="topic">{topic_str}</div>\n'
            f'  <div class="fb">\n'
            f"    <p><strong>Your reaction:</strong></p>\n"
            f"    <p>1. Does it make sense on its own? _____</p>\n"
            f"    <p>2. Right amount of info? _____</p>\n"
            f"    <p>3. Useful as a study note? _____</p>\n"
            f"    <p>4. Any other reaction? _____</p>\n"
            f"  </div>\n</div>\n"
        )

    parts.append("</body>\n</html>")

    out = root / "campaign_rerun_20260408/owner_feedback_excerpts.html"
    out.write_text("".join(parts), encoding="utf-8")

    print(f"Written {len(picks)} fresh excerpts to {out}")
    for label, e in picks:
        wc = len(e.get("primary_text", "").split())
        print(
            f"  {label}: {e['primary_function']} | {wc}w | {e['div_id']}"
            f" | SC={e['self_containment']}"
        )


if __name__ == "__main__":
    main()
