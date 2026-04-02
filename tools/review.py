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

import datetime
import hashlib
import json
import logging
import os
import sys
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("review_server")
WRITE_LOCK = threading.Lock()


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


def _comparison_pair_id(division: str, before_excerpt_id: str | None, after_excerpt_id: str | None) -> str:
    """Stable comparison pair ID derived from both sides of the pair."""
    payload = "|".join([
        division or "(root)",
        before_excerpt_id or "",
        after_excerpt_id or "",
    ])
    return "cmp_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def _comparison_key(excerpt: dict) -> str:
    """Stable comparison key, preferring div_id over display path."""
    div_id = excerpt.get("div_id")
    if isinstance(div_id, str) and div_id.strip():
        return div_id
    div_path = excerpt.get("div_path") or []
    return "/".join(div_path)


def _upsert_jsonl(path: Path, key_field: str, entry: dict) -> int:
    """Read path (JSONL), upsert entry keyed by key_field, atomic-write back.

    Returns total number of records after upsert.
    """
    with WRITE_LOCK:
        existing: dict[str, str] = {}
        dropped: list[dict[str, str | int]] = []
        if path.exists():
            with open(path, encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    stripped = line.strip()
                    if stripped:
                        try:
                            old = json.loads(stripped)
                            key = str(old[key_field])
                            existing[key] = stripped
                        except json.JSONDecodeError:
                            dropped.append({
                                "line_number": line_no,
                                "reason": "json_decode_error",
                                "raw_line": stripped,
                            })
                        except KeyError:
                            dropped.append({
                                "line_number": line_no,
                                "reason": f"missing_key:{key_field}",
                                "raw_line": stripped,
                            })
        existing[entry[key_field]] = json.dumps(entry, ensure_ascii=False)
        temp = path.with_suffix(path.suffix + ".tmp")
        with open(temp, "w", encoding="utf-8") as f:
            for line in existing.values():
                f.write(line + "\n")
        temp.replace(path)
        if dropped:
            dropped_path = path.with_name(path.name + ".dropped.jsonl")
            with open(dropped_path, "a", encoding="utf-8") as f:
                for item in dropped:
                    record = {
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "source_file": str(path),
                        **item,
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
            logger.warning(
                "Preserved %d malformed JSONL line(s) from %s in %s",
                len(dropped),
                path,
                dropped_path,
            )
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


def _read_json_file(path: Path) -> dict[str, Any] | None:
    """Best-effort JSON object reader."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _read_batch_summary(output_dir: Path) -> dict[str, Any]:
    """Read SUMMARY.json from the selected batch output dir, if present."""
    summary_path = output_dir / "SUMMARY.json"
    data = _read_json_file(summary_path)
    return data if isinstance(data, dict) else {}


def _should_open_browser() -> bool:
    """Return True when the local environment likely supports browser launch."""
    if os.environ.get("KR_REVIEW_FORCE_BROWSER") in {"1", "true", "yes"}:
        return True
    if os.environ.get("KR_REVIEW_NO_BROWSER") in {"1", "true", "yes"}:
        return False
    if os.environ.get("WSL_DISTRO_NAME"):
        return False
    if os.name == "nt":
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


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
        elif path.startswith("/api/package-state/"):
            pkg = path.split("/api/package-state/")[1].strip("/")
            if self._safe_pkg_path(pkg) is None:
                self.send_error(403, "Invalid package path")
                return
            self._api_get_package_state(pkg)
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
        summary = _read_batch_summary(self.output_dir)
        summary_packages = summary.get("packages", {}) if isinstance(summary, dict) else {}
        packages = []
        for d in sorted(self.output_dir.iterdir()):
            if not d.is_dir():
                continue
            marker_files = (
                d / "excerpts.jsonl",
                d / "progress.jsonl",
                d / "run_metadata.json",
                d / "processing_log.jsonl",
            )
            if d.name not in summary_packages and not any(path.exists() for path in marker_files):
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
            summary_entry = summary_packages.get(d.name, {}) if isinstance(summary_packages, dict) else {}
            errors = summary_entry.get("errors")
            packages.append({
                "name": d.name,
                "excerpt_count": count,
                "feedback_count": fb_count,
                "has_excerpts": excerpts_file.exists(),
                "status": summary_entry.get("status"),
                "error_count": int(summary_entry.get("error_count", 0) or 0),
                "errors": [str(error) for error in errors] if isinstance(errors, list) else [],
                "time_seconds": summary_entry.get("time_seconds"),
                "cost_estimate": summary_entry.get("cost_estimate"),
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

    def _api_get_package_state(self, pkg: str) -> None:
        """Return package status, metadata, and any timeout/stall report."""
        summary = _read_batch_summary(self.output_dir)
        summary_packages = summary.get("packages", {}) if isinstance(summary, dict) else {}
        summary_entry = summary_packages.get(pkg, {}) if isinstance(summary_packages, dict) else {}
        pkg_dir = self.output_dir / pkg
        state = {
            "name": pkg,
            "has_excerpts": (pkg_dir / "excerpts.jsonl").exists(),
            "summary": summary_entry,
            "run_metadata": _read_json_file(pkg_dir / "run_metadata.json") or {},
            "stall_report": None,
        }
        report_path = pkg_dir / "STALL_REPORT.md"
        if report_path.exists():
            try:
                state["stall_report"] = report_path.read_text(encoding="utf-8")
            except OSError:
                state["stall_report"] = None
        self._json_response(state)

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

    def _load_questionnaire(self) -> list[dict]:
        interactions_file = self.questionnaire_dir / "interactions.json"
        with open(interactions_file, encoding="utf-8") as f:
            return json.load(f)

    def _api_get_questionnaire(self) -> None:
        """Return structured questionnaire interactions from interactions.json."""
        interactions_file = self.questionnaire_dir / "interactions.json"
        if not interactions_file.exists():
            self._json_response({"error": "interactions.json not found"}, 404)
            return
        try:
            data = self._load_questionnaire()
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
        try:
            interactions = self._load_questionnaire()
        except (json.JSONDecodeError, OSError) as exc:
            self._json_response({"error": f"Cannot read interactions.json: {exc}"}, 500)
            return
        interaction = next((item for item in interactions if item.get("id") == entry["interaction_id"]), None)
        if interaction is None:
            self._json_response({"error": f"Unknown interaction_id: {entry['interaction_id']}"}, 400)
            return
        if interaction.get("availability") == "blocked_pending_source":
            self._json_response(
                {
                    "error": "Interaction is blocked pending source material",
                    "interaction_id": entry["interaction_id"],
                    "blocked_reason": interaction.get("blocked_reason"),
                },
                409,
            )
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

        Pairs are built by matching excerpts from campaign_20260331/<package> (old prompts)
        against the current output_dir <package> run (new hardened prompts) by package + division path.
        Packages without both campaign and current excerpts are skipped.
        Each pair: { pair_id, division, before: {...}, after: {...} }
        """
        repo_root = Path(__file__).parent.parent
        before_root = repo_root / "integration_tests" / "campaign_20260331"

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

        pairs: list[dict] = []
        candidate_packages = sorted(
            pkg_dir.name
            for pkg_dir in self.output_dir.iterdir()
            if pkg_dir.is_dir() and (before_root / pkg_dir.name / "excerpts.jsonl").exists()
        )

        for pkg in candidate_packages:
            before_file = before_root / pkg / "excerpts.jsonl"
            after_file = self.output_dir / pkg / "excerpts.jsonl"
            if not before_file.exists() or not after_file.exists():
                continue

            before_all = _load(before_file)
            after_all = _load(after_file)
            if not before_all or not after_all:
                continue

            after_by_div: dict[str, list[dict]] = {}
            for ex in after_all:
                key = _comparison_key(ex)
                after_by_div.setdefault(key, []).append(ex)

            used_after: set[str] = set()

            for before_ex in before_all:
                div_key = _comparison_key(before_ex)
                candidates = after_by_div.get(div_key, [])
                matched_after: dict | None = None
                for cand in candidates:
                    cid = cand.get("excerpt_id", "")
                    if cid not in used_after:
                        matched_after = cand
                        used_after.add(cid)
                        break

                comparison_scope = f"{pkg}::{div_key or '(root)'}"
                legacy_pair_id = f"legacy_{pkg}_{len(pairs)+1:03d}"
                pair_id = _comparison_pair_id(
                    comparison_scope,
                    before_ex.get("excerpt_id"),
                    matched_after.get("excerpt_id") if matched_after else None,
                )
                pairs.append({
                    "pair_id": pair_id,
                    "legacy_pair_id": legacy_pair_id,
                    "package": pkg,
                    "division": div_key or "(root)",
                    "before": {
                        "excerpt_id": before_ex.get("excerpt_id"),
                        "primary_text": before_ex.get("primary_text"),
                        "primary_function": before_ex.get("primary_function"),
                        "self_containment": before_ex.get("self_containment"),
                        "div_path": before_ex.get("div_path"),
                        "source": f"campaign_20260331/{pkg} (old prompts)",
                    },
                    "after": ({
                        "excerpt_id": matched_after.get("excerpt_id"),
                        "primary_text": matched_after.get("primary_text"),
                        "primary_function": matched_after.get("primary_function"),
                        "self_containment": matched_after.get("self_containment"),
                        "div_path": matched_after.get("div_path"),
                        "source": f"{self.output_dir.name}/{pkg} (new hardened prompts)",
                    } if matched_after else None),
                })

            for after_ex in after_all:
                after_id = after_ex.get("excerpt_id", "")
                if after_id in used_after:
                    continue
                div_key = _comparison_key(after_ex)
                comparison_scope = f"{pkg}::{div_key or '(root)'}"
                legacy_pair_id = f"legacy_{pkg}_{len(pairs)+1:03d}"
                pair_id = _comparison_pair_id(
                    comparison_scope,
                    None,
                    after_id,
                )
                pairs.append({
                    "pair_id": pair_id,
                    "legacy_pair_id": legacy_pair_id,
                    "package": pkg,
                    "division": div_key or "(root)",
                    "before": None,
                    "after": {
                        "excerpt_id": after_ex.get("excerpt_id"),
                        "primary_text": after_ex.get("primary_text"),
                        "primary_function": after_ex.get("primary_function"),
                        "self_containment": after_ex.get("self_containment"),
                        "div_path": after_ex.get("div_path"),
                        "source": f"{self.output_dir.name}/{pkg} (new hardened prompts)",
                    },
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
        logger.error("Usage: python tools/review.py <output-dir>")
        logger.error("Example: python tools/review.py integration_tests/smoke_api/")
        sys.exit(1)

    output_dir = Path(sys.argv[1]).resolve()
    if not output_dir.exists():
        logger.error("Error: %s does not exist", output_dir)
        sys.exit(1)

    viewer_html = Path(__file__).parent / "excerpt_viewer.html"
    if not viewer_html.exists():
        logger.error("Error: %s not found", viewer_html)
        sys.exit(1)

    # Questionnaire dir is always integration_tests/questionnaire/ relative to repo root
    # (one level up from tools/)
    repo_root = Path(__file__).parent.parent
    questionnaire_dir = repo_root / "integration_tests" / "questionnaire"
    if not questionnaire_dir.exists():
        logger.warning("Warning: questionnaire dir not found at %s", questionnaire_dir)
        logger.warning("Questionnaire and Comparison modes will not function.")

    ReviewHandler.output_dir = output_dir
    ReviewHandler.viewer_html = viewer_html
    ReviewHandler.questionnaire_dir = questionnaire_dir

    port = int(os.environ.get("KR_REVIEW_PORT", "8384"))
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), ReviewHandler)
    except OSError as exc:
        if getattr(exc, "errno", None) == 98:
            logger.error("Error: port %s is already in use.", port)
            logger.error("A review server is likely already running at http://127.0.0.1:%s/", port)
            logger.error("Reuse that server, stop it first, or start a new one with:")
            logger.error("  KR_REVIEW_PORT=%s python tools/review.py %s", port + 1, sys.argv[1])
            sys.exit(1)
        raise

    url = f"http://127.0.0.1:{port}/"
    logger.info("KR Excerpt Reviewer")
    logger.info("  Output dir:       %s", output_dir)
    logger.info("  Questionnaire:    %s", questionnaire_dir)
    logger.info("  Viewer:           %s", url)
    logger.info("  Feedback:         {package}/owner_feedback.jsonl")
    logger.info("  Q responses:      integration_tests/questionnaire/questionnaire_responses.jsonl")
    logger.info("  C responses:      integration_tests/questionnaire/comparison_responses.jsonl")
    logger.info("  Press Ctrl+C to stop\n")

    if _should_open_browser():
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
