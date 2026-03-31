"""KR Excerpt Review Server — live viewer + feedback writer.

Usage:
    python tools/review.py <output-dir>
    python tools/review.py integration_tests/smoke_api/

Opens browser automatically. Excerpts update live as the pipeline writes them.
Feedback saves to {output-dir}/{package}/owner_feedback.jsonl.
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


class ReviewHandler(SimpleHTTPRequestHandler):
    """Routes API requests and serves the HTML viewer."""

    output_dir: Path
    viewer_html: Path

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
        else:
            self.send_error(404)

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
        feedback = {}
        if fb_file.exists():
            with open(fb_file, encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        try:
                            entry = json.loads(stripped)
                            feedback[entry["excerpt_id"]] = entry
                        except (json.JSONDecodeError, KeyError):
                            pass
        self._json_response(feedback)

    def _api_post_feedback(self, pkg: str) -> None:
        """Append feedback entry to owner_feedback.jsonl."""
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        try:
            entry = json.loads(body)
        except json.JSONDecodeError:
            self._json_response({"error": "Invalid JSON"}, 400)
            return

        fb_file = self.output_dir / pkg / "owner_feedback.jsonl"
        try:
            fb_file.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self._json_response({"error": f"Cannot create directory: {exc}"}, 500)
            return

        # Read existing, deduplicate by excerpt_id (last entry wins)
        existing: dict[str, str] = {}
        if fb_file.exists():
            with open(fb_file, encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        try:
                            old = json.loads(stripped)
                            existing[old["excerpt_id"]] = stripped
                        except (json.JSONDecodeError, KeyError):
                            pass

        # Upsert
        existing[entry["excerpt_id"]] = json.dumps(entry, ensure_ascii=False)

        # Atomic write
        temp = fb_file.with_suffix(".jsonl.tmp")
        with open(temp, "w", encoding="utf-8") as f:
            for line in existing.values():
                f.write(line + "\n")
        temp.replace(fb_file)

        self._json_response({"ok": True, "total": len(existing)})


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

    ReviewHandler.output_dir = output_dir
    ReviewHandler.viewer_html = viewer_html

    port = int(os.environ.get("KR_REVIEW_PORT", "8384"))
    server = HTTPServer(("127.0.0.1", port), ReviewHandler)

    url = f"http://127.0.0.1:{port}/"
    print(f"KR Excerpt Reviewer")
    print(f"  Output dir: {output_dir}")
    print(f"  Viewer:     {url}")
    print(f"  Feedback:   {{package}}/owner_feedback.jsonl")
    print(f"  Press Ctrl+C to stop\n")

    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
