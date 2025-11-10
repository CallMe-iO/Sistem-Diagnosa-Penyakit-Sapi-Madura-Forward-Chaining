import pytest

from app.engine import ForwardChainingEngine
from app.storage import get_knowledge_base


@pytest.fixture(scope="module")
def engine() -> ForwardChainingEngine:
    return ForwardChainingEngine(get_knowledge_base())


def test_engine_full_match(engine: ForwardChainingEngine) -> None:
    response = engine.diagnose(["JG01", "JG02", "JG03", "JG04"], strict=True)
    assert response.diagnoses, "Expected at least one diagnosis"
    anthrax = response.diagnoses[0]
    assert anthrax.disease.code == "P1"
    assert anthrax.complete is True
    assert anthrax.missing == []


def test_engine_partial_match_in_non_strict_mode(engine: ForwardChainingEngine) -> None:
    response = engine.diagnose(["JG01"], strict=False)
    assert response.diagnoses, "Partial candidates should be returned in relaxed mode"
    assert all("JG01" in diagnosis.matched for diagnosis in response.diagnoses)
    assert any(diagnosis.missing for diagnosis in response.diagnoses)
    assert response.message == "Tidak diketahui"


def test_engine_multiple_full_matches(engine: ForwardChainingEngine) -> None:
    selected = {"JG01", "JG02", "JG03", "JG04", "JG16", "JG24"}
    response = engine.diagnose(selected, strict=True)
    codes = {diagnosis.disease.code for diagnosis in response.diagnoses}
    assert {"P1", "P7"}.issubset(codes)