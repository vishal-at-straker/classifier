"""FastAPI app: submissions router, middleware (request ID, rate limit), init DB."""
import logging
import time
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.config import get_settings
from src.db.session import init_db
from src.routers.submissions import router as submissions_router

# Structured logging: JSON in prod
def _configure_logging():
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(level=level)
    if settings.environment == "prod":
        # Optional: use python-json-logger or similar for JSON format
        pass


_configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Content Triage Agent")

# Store settings on app for routers
@app.on_event("startup")
def startup():
    app.state.settings = get_settings()
    init_db()
    logger.info("Application started")


app.include_router(submissions_router)

# Static UI for -u mode (TRIAGE AGENT header, pipeline, result, JSON)
_static_dir = Path(__file__).resolve().parent.parent / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

    @app.get("/")
    def serve_ui():
        index = _static_dir / "index.html"
        if index.exists():
            return FileResponse(index)
        return {"message": "Content Triage Agent API", "docs": "/docs"}

# CORS if needed for UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory rate limit: IP -> (count, window_start)
_rate_limit: dict[str, tuple[int, float]] = defaultdict(lambda: (0, 0.0))


@app.middleware("http")
async def add_request_id_and_rate_limit(request: Request, call_next: Callable):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    # Log with request_id (structured)
    logger.info("Request started", extra={"request_id": request_id})

    # Rate limit for POST /submissions
    if request.method == "POST" and request.url.path.rstrip("/").endswith("/submissions"):
        settings = request.app.state.settings
        client = request.client.host if request.client else "unknown"
        now = time.time()
        count, start = _rate_limit[client]
        if now - start >= settings.rate_limit_window_seconds:
            count, start = 0, now
            _rate_limit[client] = (0, now)
        if count >= settings.rate_limit_requests:
            logger.warning("Rate limit exceeded", extra={"request_id": request_id, "client": client})
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"X-Request-ID": request_id},
            )
        _rate_limit[client] = (count + 1, start)

    response = await call_next(request)
    if hasattr(request.state, "request_id"):
        response.headers["X-Request-ID"] = request.state.request_id
    return response


@app.get("/health")
def health():
    return {"status": "ok"}
