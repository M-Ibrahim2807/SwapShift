import asyncio
import logging
from contextlib import suppress

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import configure_logging
from app.services.swap_service import expire_pending_requests_job

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)
cleanup_task: asyncio.Task | None = None


async def _cleanup_loop() -> None:
    while True:
        expire_pending_requests_job()
        await asyncio.sleep(settings.request_cleanup_interval_seconds)

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    global cleanup_task
    if settings.app_env != "test":
        cleanup_task = asyncio.create_task(_cleanup_loop())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    global cleanup_task
    if cleanup_task is not None:
        cleanup_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task
        cleanup_task = None


@app.exception_handler(AppException)
async def handle_app_exception(_: Request, exc: AppException):
    logger.warning("app_exception", extra={"error_message": exc.message, "status_code": exc.status_code})
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(Exception)
async def handle_unexpected_exception(_: Request, exc: Exception):
    logger.exception("unhandled_exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")
