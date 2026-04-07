"""FastAPI application for the KR Autonomous System Dashboard.

Serves HTMX-powered pages from Jinja2 templates.
Data sourced from overnight_codex/autonomous/knowledge_base/ JSONL files.

Hardened after 3-reviewer audit (code, architecture, silent-failure-hunter).
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from scripts.autonomous_dashboard import store

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="KR Autonomous Dashboard", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# Serve HTMX locally instead of CDN (reviewer finding: offline breakage)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ═══════════════════════════════════════════════════════════════════
# Template globals — registered once, available in all templates
# ═══════════════════════════════════════════════════════════════════

def _target_label(target_value: str) -> str:
    """Human-readable DR target label."""
    labels = {
        "chatgpt_dr": "ChatGPT DR",
        "claude_dr": "Claude DR",
        "gemini_dr": "Gemini DR",
    }
    return labels.get(target_value, target_value)


def _priority_class(priority_value: str) -> str:
    """CSS class for priority badges."""
    return f"badge-{priority_value}"


def _severity_class(severity_value: str) -> str:
    """CSS class for severity badges."""
    return f"badge-{severity_value}"


templates.env.globals["target_label"] = _target_label
templates.env.globals["priority_class"] = _priority_class
templates.env.globals["severity_class"] = _severity_class


# ═══════════════════════════════════════════════════════════════════
# Global error handler — return HTML, not JSON (reviewer finding #5/#6)
# ═══════════════════════════════════════════════════════════════════

@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException) -> HTMLResponse:
    """Render 404, 405 etc. as HTML instead of JSON."""
    return templates.TemplateResponse("error.html", {
        "request": request,
        "page": "error",
        "error_message": f"Page not found ({exc.status_code})" if exc.status_code == 404 else str(exc.detail),
    }, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> HTMLResponse:
    """Render form validation errors as HTML instead of JSON."""
    return templates.TemplateResponse("error.html", {
        "request": request,
        "page": "error",
        "error_message": "Invalid form submission. Please go back and try again.",
    }, status_code=422)


@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception) -> HTMLResponse:
    """Catch-all: render unexpected errors as HTML."""
    logger.error("Dashboard error on %s: %s", request.url.path, exc, exc_info=True)
    return templates.TemplateResponse("error.html", {
        "request": request,
        "page": "error",
        "error_message": str(exc),
    }, status_code=500)


# ═══════════════════════════════════════════════════════════════════
# Pages
# ═══════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def relay_queue(request: Request) -> HTMLResponse:
    """DR Relay Queue — the most important page."""
    prompts, errors = store.load_all_prompts()
    stats = store.get_relay_stats()
    return templates.TemplateResponse("relay.html", {
        "request": request,
        "page": "relay",
        "prompts": prompts,
        "stats": stats,
        "data_errors": errors,
    })


@app.get("/findings", response_class=HTMLResponse)
async def findings_page(request: Request) -> HTMLResponse:
    """Findings page — grouped by severity."""
    grouped, errors = store.get_findings_by_severity()
    stats = store.get_findings_stats()
    return templates.TemplateResponse("findings.html", {
        "request": request,
        "page": "findings",
        "grouped": grouped,
        "stats": stats,
        "data_errors": errors,
    })


@app.get("/ideas", response_class=HTMLResponse)
async def ideas_page(request: Request) -> HTMLResponse:
    """Ideas page — list + submission form."""
    ideas = store.load_ideas()
    return templates.TemplateResponse("ideas.html", {
        "request": request,
        "page": "ideas",
        "ideas": ideas,
        "error_message": "",
        "prefill_title": "",
        "prefill_desc": "",
    })


@app.post("/ideas/submit", response_model=None)
async def submit_idea(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
) -> HTMLResponse | RedirectResponse:
    """Handle idea submission with error recovery (reviewer finding #1/#3)."""
    try:
        store.submit_idea(title=title, description=description)
        return RedirectResponse(url="/ideas", status_code=303)
    except OSError as e:
        logger.error("Failed to save idea: %s", e)
        ideas = store.load_ideas()
        return templates.TemplateResponse("ideas.html", {
            "request": request,
            "page": "ideas",
            "ideas": ideas,
            "error_message": f"Could not save your idea: {e}. Please try again.",
            "prefill_title": title,
            "prefill_desc": description,
        }, status_code=500)


@app.get("/status", response_class=HTMLResponse)
async def status_page(request: Request) -> HTMLResponse:
    """Status page — pipeline health and research progress."""
    relay_stats = store.get_relay_stats()
    findings_stats = store.get_findings_stats()
    gaps_stats = store.get_gaps_stats()
    dr_stats = store.get_dr_response_stats()
    return templates.TemplateResponse("status.html", {
        "request": request,
        "page": "status",
        "relay_stats": relay_stats,
        "findings_stats": findings_stats,
        "gaps_stats": gaps_stats,
        "dr_stats": dr_stats,
    })
