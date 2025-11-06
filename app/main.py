"""Bootstrap module for running the FastAPI application."""
from __future__ import annotations

from fastapi import FastAPI

from . import api

app = FastAPI(
    title="Sistem Pakar Diagnosa Penyakit Sapi",
    version="1.0.0",
    description="Layanan REST sederhana untuk diagnosa penyakit sapi berbasis forward chaining.",
)

app.include_router(api.router)


__all__ = ["app"]