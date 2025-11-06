"""Utility helpers to load and cache the knowledge base JSON file."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from .models import KnowledgeBase

BASE_DIR = Path(__file__).resolve().parent.parent
KB_PATH = BASE_DIR / "knowledge_base.json"


@lru_cache(maxsize=1)
def get_knowledge_base() -> KnowledgeBase:
    """Load and cache the knowledge base for reuse across requests."""

    if not KB_PATH.exists():
        raise FileNotFoundError(f"Knowledge base file not found at {KB_PATH}")
    return KnowledgeBase.parse_file(KB_PATH)


def get_symptom_codes() -> set[str]:
    """Return a set of every known symptom code."""

    kb = get_knowledge_base()
    return {symptom.code for symptom in kb.symptoms}