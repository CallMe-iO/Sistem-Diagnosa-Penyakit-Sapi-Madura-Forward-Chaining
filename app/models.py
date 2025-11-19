"""Model Pydantic yang dipakai layanan diagnosa penyakit sapi."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, validator


class Symptom(BaseModel):
    """Merepresentasikan satu gejala yang terdaftar pada basis pengetahuan."""

    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class Disease(BaseModel):
    """Menjelaskan satu penyakit lengkap dengan daftar gejala yang wajib terpenuhi."""

    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    symptoms: List[str] = Field(..., min_items=1)


class KnowledgeBase(BaseModel):
    """Skema lengkap untuk file JSON basis pengetahuan yang dimuat engine."""

    symptoms: List[Symptom]
    diseases: List[Disease]


class DiagnoseRequest(BaseModel):
    """Payload yang dikirim ke endpoint /api/diagnose berisi gejala pilihan pengguna."""

    selected: List[str] = Field(default_factory=list, description="List of symptom codes selected by the user")

    @validator("selected", pre=True)
    def _normalize_selected(cls, value: Optional[List[str]]) -> List[str]:  # noqa: D401
        """Menjamin daftar kode selalu unik dan berformat huruf kapital agar konsisten."""

        if value is None:
            return []
        unique_codes = []
        for code in value:
            if not isinstance(code, str):
                raise ValueError("Symptom codes must be strings")
            normalized = code.strip().upper()
            if normalized and normalized not in unique_codes:
                unique_codes.append(normalized)
        return unique_codes


class DiagnosisResult(BaseModel):
    """Rincian evaluasi penyakit setelah aturan forward chaining dijalankan."""

    disease: Disease
    matched: List[str]
    missing: List[str]
    complete: bool


class DiagnoseResponse(BaseModel):
    """Struktur respons resmi yang dikirim endpoint /api/diagnose ke klien."""

    diagnoses: List[DiagnosisResult]
    message: Optional[str] = None
