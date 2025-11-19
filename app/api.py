"""FastAPI routers for the diagnosis API and simple UI."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

try:
    # Default to package-relative imports when running via `uvicorn app.main:app`
    from .engine import ForwardChainingEngine
    from .models import DiagnoseRequest, DiagnoseResponse, Symptom
    from .storage import get_knowledge_base, get_symptom_codes
except ImportError:  # pragma: no cover - fallback for script execution
    from engine import ForwardChainingEngine  # type: ignore
    from models import DiagnoseRequest, DiagnoseResponse, Symptom  # type: ignore
    from storage import get_knowledge_base, get_symptom_codes  # type: ignore

router = APIRouter()


def get_engine() -> ForwardChainingEngine:
    """Return a singleton engine instance."""

    kb = get_knowledge_base()
    return ForwardChainingEngine(kb)


@router.get("/api/symptoms", response_model=List[Symptom])
def list_symptoms() -> List[Symptom]:
    """Expose every symptom to power the UI."""

    return get_knowledge_base().symptoms


@router.post("/api/diagnose", response_model=DiagnoseResponse)
def diagnose(payload: DiagnoseRequest, strict: bool = Query(False, description="Hanya tampilkan rule lengkap")) -> DiagnoseResponse:
    """Evaluate the provided symptoms and return diagnoses."""

    known_codes = get_symptom_codes()
    unknown = sorted(set(payload.selected) - known_codes)
    if unknown:
        detail = {
            "error": "Kode gejala tidak dikenal",
            "invalid": unknown,
        }
        raise HTTPException(status_code=422, detail=detail)

    engine = get_engine()
    response = engine.diagnose(payload.selected, strict=strict)
    if not response.diagnoses:
        response.message = "Tidak diketahui"
    return response


@router.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    """Serve a minimal UI for manual testing."""

    html = """
    <!doctype html>
    <html lang=\"id\">
    <head>
        <meta charset=\"utf-8\" />
        <title>Sistem Pakar Diagnosa Penyakit Sapi Madura</title>
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <style>
            body { font-family: Arial, sans-serif; margin: 2rem; }
            fieldset { border: 1px solid #ccc; padding: 1rem; }
            legend { font-weight: bold; }
            .symptom { margin-bottom: 0.35rem; display: inline-flex; align-items: center; gap: 0.35rem; }
            button { margin-top: 1rem; padding: 0.6rem 1rem; cursor: pointer; }
            #result { margin-top: 1.5rem; }
            .result-card { border: 1px solid #e0e0e0; border-radius: 6px; padding: 1rem; margin-bottom: 1rem; background: #fafafa; }
            .status { font-weight: bold; margin: 0.25rem 0 0.75rem; }
            .status-complete { color: #0a845e; }
            .status-partial { color: #c27803; }
            .empty { color: #666; font-style: italic; }
        </style>
    </head>
    <body>
        <h1>Sistem Pakar Diagnosa Penyakit Sapi Madura</h1>
        <p>Pilih gejala yang terlihat kemudian tekan <strong>Diagnosa</strong>.</p>
        <label><input type=\"checkbox\" id=\"strict\" /> Mode ketat (rule lengkap saja)</label>
        <form id=\"diagnosis-form\">
            <fieldset id=\"symptom-list\">
                <legend>Daftar Gejala</legend>
            </fieldset>
            <button type=\"submit\">Diagnosa</button>
        </form>
        <h2>Hasil</h2>
        <div id=\"result\" class=\"empty\">Belum ada data</div>
        <script>
        let symptomLookup = new Map();

        async function fetchSymptoms() {
            const res = await fetch('/api/symptoms');
            const symptoms = await res.json();
            symptomLookup = new Map(symptoms.map(item => [item.code, item.name]));
            const container = document.getElementById('symptom-list');
            symptoms.forEach(symptom => {
                const label = document.createElement('label');
                label.className = 'symptom';
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = symptom.code;
                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(symptom.name));
                container.appendChild(label);
                container.appendChild(document.createElement('br'));
            });
        }

        function formatSymptoms(codes) {
            if (!codes.length) {
                return 'Tidak ada';
            }
            return codes.map(code => symptomLookup.get(code) || code).join(', ');
        }

        function renderResult(payload) {
            const container = document.getElementById('result');
            container.classList.remove('empty');
            container.innerHTML = '';

            if (!payload.diagnoses.length) {
                const message = payload.message || 'Tidak diketahui';
                container.classList.add('empty');
                container.textContent = message;
                return;
            }

            payload.diagnoses.forEach(entry => {
                const card = document.createElement('article');
                card.className = 'result-card';
                card.innerHTML = `
                    <h3>${entry.disease.name}</h3>
                    <p class="status ${entry.complete ? 'status-complete' : 'status-partial'}">
                        ${entry.complete ? 'Kecocokan penuh' : 'Masih membutuhkan gejala lain'}
                    </p>
                    <p><strong>Gejala terpenuhi:</strong> ${formatSymptoms(entry.matched)}</p>
                    <p><strong>Perlu diperiksa:</strong> ${entry.missing.length ? formatSymptoms(entry.missing) : 'Tidak ada'}</p>
                `;
                container.appendChild(card);
            });
        }

        document.getElementById('diagnosis-form').addEventListener('submit', async (event) => {
            event.preventDefault();
            const selected = Array.from(document.querySelectorAll('#symptom-list input:checked'))
                .map(el => el.value);
            const strictMode = document.getElementById('strict').checked;
            const res = await fetch(`/api/diagnose?strict=${strictMode}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ selected }),
            });
            const payload = await res.json();
            renderResult(payload);
        });

        fetchSymptoms();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
