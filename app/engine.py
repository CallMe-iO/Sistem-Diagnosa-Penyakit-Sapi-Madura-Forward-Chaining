"""Forward chaining inference engine for cattle disease diagnosis."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .models import DiagnoseResponse, DiagnosisResult, Disease, KnowledgeBase


@dataclass
class Evaluation:
    """Internal representation of a disease evaluation."""

    disease: Disease
    matched: List[str]
    missing: List[str]

    @property
    def complete(self) -> bool:
        return not self.missing


class ForwardChainingEngine:
    """Simple forward chaining engine using subset evaluation."""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base

    def diagnose(self, selected: Iterable[str], *, strict: bool = False) -> DiagnoseResponse:
        """Run the engine and return a structured response."""

        selected_set = {code.upper() for code in selected}
        evaluations = [self._evaluate_rule(disease, selected_set) for disease in self.knowledge_base.diseases]

        if strict:
            filtered = [evaluation for evaluation in evaluations if evaluation.complete]
        else:
            filtered = [evaluation for evaluation in evaluations if evaluation.matched]

        diagnoses = [
            DiagnosisResult(
                disease=evaluation.disease,
                matched=evaluation.matched,
                missing=evaluation.missing,
                complete=evaluation.complete,
            )
            for evaluation in filtered
        ]

        message = None if any(result.complete for result in diagnoses) else "Tidak diketahui"
        return DiagnoseResponse(diagnoses=diagnoses, message=message)

    def _evaluate_rule(self, disease: Disease, selected: set[str]) -> Evaluation:
        """Compute which required symptoms are present."""

        required = list(dict.fromkeys(disease.symptoms))
        matched = sorted(code for code in required if code in selected)
        missing = sorted(code for code in required if code not in selected)
        return Evaluation(disease=disease, matched=matched, missing=missing)


__all__ = ["ForwardChainingEngine"]
