"""Bootstrap module for running the FastAPI application."""
from __future__ import annotations

from fastapi import FastAPI

try:
    # Prefer package-relative import when running `uvicorn app.main:app`
    from . import api
except ImportError:  # pragma: no cover - fallback when run as a script
    import api  # type: ignore

app = FastAPI(
    title="Sistem Pakar Diagnosa Penyakit Sapi",
    version="1.0.0",
    description="Layanan REST sederhana untuk diagnosa penyakit sapi berbasis forward chaining.",
)

app.include_router(api.router)


__all__ = ["app"]
