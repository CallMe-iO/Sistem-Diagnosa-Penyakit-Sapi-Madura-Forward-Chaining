"""Kumpulan utilitas untuk memuat serta menyimpan cache file basis pengetahuan JSON."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

try:
    from .models import KnowledgeBase
except ImportError:  # pragma: no cover - fallback for script execution
    from models import KnowledgeBase  # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent
KB_PATH = BASE_DIR / "knowledge_base.json"


@lru_cache(maxsize=1)
def get_knowledge_base() -> KnowledgeBase:
    """Memuat basis pengetahuan lalu menyimpannya di cache agar permintaan berikutnya lebih cepat."""

    if not KB_PATH.exists():
        raise FileNotFoundError(f"Knowledge base file not found at {KB_PATH}")
    return KnowledgeBase.parse_file(KB_PATH)


def get_symptom_codes() -> set[str]:
    """Mengembalikan himpunan kode gejala yang valid sebagai referensi pengecekan input."""

    kb = get_knowledge_base()
    return {symptom.code for symptom in kb.symptoms}
                                                                                                                              