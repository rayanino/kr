"""KR Excerpt Review Server — live viewer + feedback writer.

Usage:
    python tools/review.py <output-dir>
    python tools/review.py integration_tests/smoke_api/

Opens browser automatically. Excerpts update live as the pipeline writes them.
Feedback saves to {output-dir}/{package}/owner_feedback.jsonl.

Additional modes served from integration_tests/questionnaire/:
  GET  /api/questionnaire            — 40 structured interactions
  GET  /api/questionnaire/responses  — all saved responses (keyed by id)
  POST /api/questionnaire/response   — upsert one response
  GET  /api/comparisons              — comparison pairs (before/after excerpts)
  GET  /api/comparison/responses     — all saved comparison verdicts
  POST /api/comparison/response      — upsert one comparison verdict
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import webbrowser
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _content_hash(excerpt: dict) -> str:
    """SHA-256 of key fields — detects stale feedback on changed excerpts."""
    payload = (
        (excerpt.get("primary_text") or "")
        + "|"
        + (excerpt.get("primary_function") or "")
        + "|"
        + (excerpt.get("self_containment") or "")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def _upsert_jsonl(path: Path, key_field: str, entry: dict) -> int:
    """Read path (JSONL), upsert entry keyed by key_field, atomic-write back.

    Returns total number of records after upsert.
    """
    existing: dict[str, str] = {}
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    try:
                        old = json.loads(stripped)
                        existing[old[key_field]] = stripped
                    except (json.JSONDecodeError, KeyError):
                        pass
    existing[entry[key_field]] = json.dumps(entry, ensure_ascii=False)
    temp = path.with_suffix(path.suffix + ".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        for line in existing.values():
            f.write(line + "\n")
    temp.replace(path)
    return len(existing)


def _read_jsonl_keyed(path: Path, key_field: str) -> dict:
    """Read a JSONL file and return a dict keyed by key_field."""
    result: dict = {}
    if not path.exists():
        return result
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                try:
                    entry = json.loads(stripped)
                    result[entry[key_field]] = entry
                except (json.JSONDecodeError, KeyError):
                    pass
    return result


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class ReviewHandler(SimpleHTTPRequestHandler):
    """Routes API requests and serves the HTML viewer."""

    output_dir: Path
    viewer_html: Path
    questionnaire_dir: Path  # integration_tests/questionnaire/

    def log_message(self, fmt: str, *args: object) -> None:
        # Quieter logging — only show API calls
        msg = fmt % args
        if "/api/" in msg or "POST" in msg:
            sys.stderr.write(f"[review] {msg}\n")

    def _safe_pkg_path(self, pkg: str) -> Path | None:
        """Validate package name — prevent path traversal (Gemini review flag)."""
        requested = (self.output_dir / pkg).resolve()
        if not requested.is_relative_to(self.output_dir.resolve()):
            return None
        if not requested.is_dir():
            return None
        return requested

    # ------------------------------------------------------------------ routing

    def do_GET(self) -> None:
        path = unquote(self.path).split("?")[0]

        if path == "/" or path == "":
            self._serve_html()
        elif path == "/api/packages":
            self._api_packages()
        elif path.startswith("/api/excerpts/"):
            pkg = path.split("/api/excerpts/")[1].strip("/")
            if self._safe_pkg_path(pkg) is None:
                self.send_error(403, "Invalid package path")
                return
            self._api_excerpts(pkg)
        elif path.startswith("/api/feedback/"):
            pkg = path.split("/api/feedback/")[1].strip("/")
            if self._safe_pkg_path(pkg) is None:
                self.send_error(403, "Invalid package path")
                return
            self._api_get_feedback(pkg)
        # ── Questionnaire endpoints ──────────────────────────────────────────
        elif path == "/api/questionnaire":
            self._api_get_questionnaire()
        elif path == "/api/questionnaire/responses":
            self._api_get_questionnaire_responses()
        # ── Comparison endpoints ─────────────────────────────────────────────
        elif path == "/api/comparisons":
            self._api_get_comparisons()
        elif path == "/api/comparison/responses":
            self._api_get_comparison_responses()
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        path = unquote(self.path).split("?")[0]
        if path.startswith("/api/feedback/"):
            pkg = path.split("/api/feedback/")[1].strip("/")
            if self._safe_pkg_path(pkg) is None:
                self.send_error(403, "Invalid package path")
                return
            self._api_post_feedback(pkg)
        elif path == "/api/questionnaire/response":
            self._api_post_questionnaire_response()
        elif path == "/api/comparison/response":
            self._api_post_comparison_response()
        else:
            self.send_error(404)

    # ------------------------------------------------------------------ helpers

    def _serve_html(self) -> None:
        content = self.viewer_html.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _json_response(self, data: object, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict | None:
        """Read and parse JSON request body. Returns None on error."""
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            self._json_response({"error": "Invalid JSON"}, 400)
            return None

    # ------------------------------------------------------------------ review endpoints (unchanged)

    def _api_packages(self) -> None:
        """List packages with excerpt counts."""
        packages = []
        for d in sorted(self.output_dir.iterdir()):
            if not d.is_dir():
                continue
            excerpts_file = d / "excerpts.jsonl"
            count = 0
            if excerpts_file.exists():
                with open(excerpts_file, encoding="utf-8") as f:
                    count = sum(1 for line in f if line.strip())
            fb_file = d / "owner_feedback.jsonl"
            fb_count = 0
            if fb_file.exists():
                with open(fb_file, encoding="utf-8") as f:
                    fb_count = sum(1 for line in f if line.strip())
            packages.append({
                "name": d.name,
                "excerpt_count": count,
                "feedback_count": fb_count,
                "has_excerpts": excerpts_file.exists(),
            })
        self._json_response(packages)

    def _api_excerpts(self, pkg: str) -> None:
        """Read excerpts.jsonl live from disk."""
        excerpts_file = self.output_dir / pkg / "excerpts.jsonl"
        if not excerpts_file.exists():
            self._json_response([], 200)
            return
        excerpts = []
        with open(excerpts_file, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    try:
                        ex = json.loads(stripped)
                        ex["_content_hash"] = _content_hash(ex)
                        excerpts.append(ex)
                    except json.JSONDecodeError:
                        pass
        self._json_response(excerpts)

    def _api_get_feedback(self, pkg: str) -> None:
        """Read existing feedback."""
        fb_file = self.output_dir / pkg / "owner_feedback.jsonl"
        feedback = _read_jsonl_keyed(fb_file, "excerpt_id")
        self._json_response(feedback)

    def _api_post_feedback(self, pkg: str) -> None:
        """Append feedback entry to owner_feedback.jsonl."""
        entry = self._read_body()
        if entry is None:
            return

        fb_file = self.output_dir / pkg / "owner_feedback.jsonl"
        try:
            fb_file.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self._json_response({"error": f"Cannot create directory: {exc}"}, 500)
            return

        total = _upsert_jsonl(fb_file, "excerpt_id", entry)
        self._json_response({"ok": True, "total": total})

    # ------------------------------------------------------------------ questionnaire endpoints

    def _api_get_questionnaire(self) -> None:
        """Return the 40 structured interactions from interactions.json."""
        interactions_file = self.questionnaire_dir / "interactions.json"
        if not interactions_file.exists():
            self._json_response({"error": "interactions.json not found"}, 404)
            return
        try:
            with open(interactions_file, encoding="utf-8") as f:
                data = json.load(f)
            self._json_response(data)
        except (json.JSONDecodeError, OSError) as exc:
            self._json_response({"error": str(exc)}, 500)

    def _api_get_questionnaire_responses(self) -> None:
        """Return all saved questionnaire responses keyed by interaction id."""
        responses_file = self.questionnaire_dir / "questionnaire_responses.jsonl"
        responses = _read_jsonl_keyed(responses_file, "interaction_id")
        self._json_response(responses)

    def _api_post_questionnaire_response(self) -> None:
        """Upsert one questionnaire response."""
        entry = self._read_body()
        if entry is None:
            return
        if "interaction_id" not in entry:
            self._json_response({"error": "Missing interaction_id"}, 400)
            return

        responses_file = self.questionnaire_dir / "questionnaire_responses.jsonl"
        try:
            responses_file.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self._json_response({"error": f"Cannot create directory: {exc}"}, 500)
            return

        total = _upsert_jsonl(responses_file, "interaction_id", entry)
        self._json_response({"ok": True, "total": total})

    # ------------------------------------------------------------------ comparison endpoints

    def _api_get_comparisons(self) -> None:
        """Return before/after comparison pairs.

        Pairs are built by matching excerpts from smoke_api/taysir (new hardened prompts)
        against campaign_20260331/taysir (old prompts) by div_path position.
        Each pair: { pair_id, division, before: {...}, after: {...} }
        """
        # Comparison: current output_dir has "after" (v2), campaign has "before"
        # output_dir is e.g. integration_tests/smoke_api_v2/
        # campaign is always at integration_tests/campaign_20260331/ (sibling)
        repo_root = self.output_dir.parent.parent  # integration_tests/../ = repo root
        after_file = self.output_dir / "taysir" / "excerpts.jsonl"
        before_file = repo_root / "integration_tests" / "campaign_20260331" / "taysir" / "excerpts.jsonl"

        def _load(path: Path) -> list[dict]:
            items: list[dict] = []
            if not path.exists():
                return items
            with open(path, encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        try:
                            items.append(json.loads(stripped))
                        except json.JSONDecodeError:
                            pass
            return items

        before_all = _load(before_file)
        after_all = _load(after_file)

        # Index after-excerpts by div_path string for fast lookup
        after_by_div: dict[str, list[dict]] = {}
        for ex in after_all:
            key = "/".join(ex.get("div_path") or [])
            after_by_div.setdefault(key, []).append(ex)

        pairs: list[dict] = []
        used_after: set[str] = set()

        for before_ex in before_all:
            div_key = "/".join(before_ex.get("div_path") or [])
            candidates = after_by_div.get(div_key, [])
            # Pick the first unused candidate in the same division
            matched_after: dict | None = None
            for cand in candidates:
                cid = cand.get("excerpt_id", "")
                if cid not in used_after:
                    matched_after = cand
                    used_after.add(cid)
                    break

            pair_id = f"pair_{len(pairs)+1:03d}"
            pairs.append({
                "pair_id": pair_id,
                "division": div_key or "(root)",
                "before": {
                    "excerpt_id": before_ex.get("excerpt_id"),
                    "primary_text": before_ex.get("primary_text"),
                    "primary_function": before_ex.get("primary_function"),
                    "self_containment": before_ex.get("self_containment"),
                    "div_path": before_ex.get("div_path"),
                    "source": "smoke_api/taysir (new prompts)",
                },
                "after": {
                    "excerpt_id": matched_after.get("excerpt_id") if matched_after else None,
                    "primary_text": matched_after.get("primary_text") if matched_after else None,
                    "primary_function": matched_after.get("primary_function") if matched_after else None,
                    "self_containment": matched_after.get("self_containment") if matched_after else None,
                    "div_path": matched_after.get("div_path") if matched_after else None,
                    "source": "campaign_20260331/taysir (old prompts)" if matched_after else None,
                } if matched_after else None,
            })

        self._json_response(pairs)

    def _api_get_comparison_responses(self) -> None:
        """Return all saved comparison verdicts keyed by pair_id."""
        responses_file = self.questionnaire_dir / "comparison_responses.jsonl"
        responses = _read_jsonl_keyed(responses_file, "pair_id")
        self._json_response(responses)

    def _api_post_comparison_response(self) -> None:
        """Upsert one comparison verdict."""
        entry = self._read_body()
        if entry is None:
            return
        if "pair_id" not in entry:
            self._json_response({"error": "Missing pair_id"}, 400)
            return

        responses_file = self.questionnaire_dir / "comparison_responses.jsonl"
        try:
            responses_file.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self._json_response({"error": f"Cannot create directory: {exc}"}, 500)
            return

        total = _upsert_jsonl(responses_file, "pair_id", entry)
        self._json_response({"ok": True, "total": total})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tools/review.py <output-dir>")
        print("Example: python tools/review.py integration_tests/smoke_api/")
        sys.exit(1)

    output_dir = Path(sys.argv[1]).resolve()
    if not output_dir.exists():
        print(f"Error: {output_dir} does not exist")
        sys.exit(1)

    viewer_html = Path(__file__).parent / "excerpt_viewer.html"
    if not viewer_html.exists():
        print(f"Error: {viewer_html} not found")
        sys.exit(1)

    # Questionnaire dir is always integration_tests/questionnaire/ relative to repo root
    # (one level up from tools/)
    repo_root = Path(__file__).parent.parent
    questionnaire_dir = repo_root / "integration_tests" / "questionnaire"
    if not questionnaire_dir.exists():
        print(f"Warning: questionnaire dir not found at {questionnaire_dir}")
        print("Questionnaire and Comparison modes will not function.")

    ReviewHandler.output_dir = output_dir
    ReviewHandler.viewer_html = viewer_html
    ReviewHandler.questionnaire_dir = questionnaire_dir

    port = int(os.environ.get("KR_REVIEW_PORT", "8384"))
    server = HTTPServer(("127.0.0.1", port), ReviewHandler)

    url = f"http://127.0.0.1:{port}/"
    print(f"KR Excerpt Reviewer")
    print(f"  Output dir:       {output_dir}")
    print(f"  Questionnaire:    {questionnaire_dir}")
    print(f"  Viewer:           {url}")
    print(f"  Feedback:         {{package}}/owner_feedback.jsonl")
    print(f"  Q responses:      integration_tests/questionnaire/questionnaire_responses.jsonl")
    print(f"  C responses:      integration_tests/questionnaire/comparison_responses.jsonl")
    print(f"  Press Ctrl+C to stop\n")

    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
