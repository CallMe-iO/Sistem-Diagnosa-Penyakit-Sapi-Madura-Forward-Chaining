"""Pydantic models for the cattle disease diagnosis service."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, validator


class Symptom(BaseModel):
    """Represents a possible symptom in the knowledge base."""

    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class Disease(BaseModel):
    """Represents a disease rule and its prerequisite symptoms."""

    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    symptoms: List[str] = Field(..., min_items=1)


class KnowledgeBase(BaseModel):
    """Concrete schema for the JSON knowledge base file."""

    symptoms: List[Symptom]
    diseases: List[Disease]


class DiagnoseRequest(BaseModel):
    """Payload received from /api/diagnose."""

    selected: List[str] = Field(default_factory=list, description="List of symptom codes selected by the user")

    @validator("selected", pre=True)
    def _normalize_selected(cls, value: Optional[List[str]]) -> List[str]:  # noqa: D401
        """Ensure we always work with a list of unique, upper-cased codes."""

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
    """Details of a disease evaluation run."""

    disease: Disease
    matched: List[str]
    missing: List[str]
    complete: bool


class DiagnoseResponse(BaseModel):
    """API response emitted by /api/diagnose."""

    diagnoses: List[DiagnosisResult]
    message: Optional[str] = None