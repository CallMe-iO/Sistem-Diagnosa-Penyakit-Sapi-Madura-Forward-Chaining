"""Router FastAPI yang menyediakan endpoint diagnosa serta UI sederhana."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

try:
    # Standar impor relatif paket ketika aplikasi dijalankan lewat `uvicorn app.main:app`
    from .engine import ForwardChainingEngine
    from .models import DiagnoseRequest, DiagnoseResponse, Symptom
    from .storage import get_knowledge_base, get_symptom_codes
except ImportError:  # pragma: no cover - fallback for script execution
    from engine import ForwardChainingEngine  # type: ignore
    from models import DiagnoseRequest, DiagnoseResponse, Symptom  # type: ignore
    from storage import get_knowledge_base, get_symptom_codes  # type: ignore

router = APIRouter()


def get_engine() -> ForwardChainingEngine:
    """Mengembalikan satu-satunya instance mesin inferensi agar dapat dipakai ulang."""

    kb = get_knowledge_base()
    return ForwardChainingEngine(kb)

 
@router.get("/api/symptoms", response_model=List[Symptom])
def list_symptoms() -> List[Symptom]:
    """Menyediakan seluruh daftar gejala untuk mengisi antarmuka pengguna."""

    return get_knowledge_base().symptoms


@router.post("/api/diagnose", response_model=DiagnoseResponse)
def diagnose(payload: DiagnoseRequest, strict: bool = Query(False, description="Hanya tampilkan rule lengkap")) -> DiagnoseResponse:
    """Menjalankan evaluasi forward chaining atas gejala terpilih dan mengembalikan hasil diagnosa."""

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
    """Menyajikan UI minimalis yang membantu pengujian manual via browser."""

    html = """
    <!doctype html>
    <html lang="id">
    <head>
        <meta charset="utf-8" />
        <title>Sistem Pakar Diagnosa Penyakit Sapi Madura</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <style>
            body { background: #f5f7fb; }
            .card { border: none; border-radius: 1rem; }
            .card-header { border-bottom: none; background: transparent; }
            .symptom-checkbox { background: #fff; border-radius: 0.75rem; padding: 0.35rem 0.75rem; }
            .result-card { border-radius: 0.85rem; }
            .badge-soft-success { background: rgba(25, 135, 84, 0.15); color: #198754; }
            .badge-soft-warning { background: rgba(255, 193, 7, 0.2); color: #b7791f; }
            .empty-state { color: #6c757d; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="container py-4 py-lg-5">
            <div class="text-center mb-4">
                <h1 class="display-6 fw-semibold">Sistem Pakar Diagnosa Penyakit Sapi Madura</h1>
                <p class="text-muted mb-0">Pilih gejala yang terlihat lalu klik <strong>Diagnosa</strong> untuk melihat kemungkinan penyakit.</p>
            </div>
            <div class="row g-4 align-items-start"><!-- UI: layout form gejala dan hasil diagnosa -->
                <div class="col-12 col-md-5">
                    <div class="card shadow-sm h-100">
                        <div class="card-header pb-0">
                            <h2 class="h5 mb-1">Daftar Gejala</h2>
                            <p class="text-muted small mb-3">Centang gejala yang dialami sapi.</p>
                        </div>
                        <div class="card-body">
                            <div class="d-flex align-items-center justify-content-between bg-light rounded-3 px-3 py-2 mb-3">
                                <div>
                                    <p class="mb-0 fw-semibold">Mode ketat</p>
                                    <small class="text-muted">Hanya tampilkan rule lengkap</small>
                                </div>
                                <div class="form-check form-switch m-0">
                                    <input class="form-check-input" type="checkbox" id="strict">
                                </div>
                            </div>
                            <form id="diagnosis-form">
                                <div id="symptom-list" class="row row-cols-1 row-cols-lg-2 g-2 mb-3"></div>
                                <button type="submit" class="btn btn-primary w-100">Diagnosa</button>
                            </form>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-7">
                    <div class="card shadow-sm h-100">
                        <div class="card-header pb-0">
                            <h2 class="h5 mb-1">Hasil Diagnosa</h2>
                            <p class="text-muted small mb-3">Hasil akan ditampilkan di sini setelah proses diagnosa.</p>
                        </div>
                        <div class="card-body">
                            <div id="result" class="empty-state text-center py-5">Belum ada data</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script>
        let symptomLookup = new Map();

        async function fetchSymptoms() {
            const res = await fetch('/api/symptoms');
            const symptoms = await res.json();
            symptomLookup = new Map(symptoms.map(item => [item.code, item.name]));
            const container = document.getElementById('symptom-list');
            symptoms.forEach(symptom => {
                const wrapper = document.createElement('div');
                const formCheck = document.createElement('div');
                formCheck.className = 'form-check symptom-checkbox';
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = symptom.code;
                checkbox.id = `symptom-${symptom.code}`;
                checkbox.className = 'form-check-input';
                const label = document.createElement('label');
                label.className = 'form-check-label fw-medium';
                label.setAttribute('for', checkbox.id);
                label.textContent = symptom.name;
                formCheck.appendChild(checkbox);
                formCheck.appendChild(label);
                wrapper.appendChild(formCheck);
                container.appendChild(wrapper);
            });
        }

        function formatSymptoms(codes) {
            if (!codes.length) {
                return 'Tidak ada';
            }
            return codes.map(code => symptomLookup.get(code) || code).join(', ');
        }

        function calculateScore(entry) {
            const total = entry.matched.length + entry.missing.length;
            if (!total) {
                return 0;
            }
            return entry.matched.length / total;
        }

        function renderResult(payload) {
            const container = document.getElementById('result');
            container.classList.remove('empty-state', 'text-center', 'py-5');
            container.innerHTML = '';

            if (!payload.diagnoses.length) {
                const message = payload.message || 'Tidak diketahui';
                container.classList.add('empty-state', 'text-center', 'py-5');
                container.textContent = message;
                return;
            }

            const results = [...payload.diagnoses];
            results.sort((a, b) => { // Sorting: tampilkan hasil dengan kecocokan penuh terlebih dahulu
                if (a.complete !== b.complete) {
                    return a.complete ? -1 : 1;
                }
                const scoreDiff = calculateScore(b) - calculateScore(a);
                if (scoreDiff !== 0) {
                    return scoreDiff;
                }
                return b.matched.length - a.matched.length;
            });

            results.forEach(entry => {
                const card = document.createElement('div');
                card.className = 'result-card border bg-white shadow-sm p-3 mb-3';
                const badgeClass = entry.complete ? 'badge badge-soft-success' : 'badge badge-soft-warning';
                const badgeText = entry.complete ? 'Kecocokan penuh' : 'Masih membutuhkan gejala lain';
                card.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h3 class="h5 mb-0">${entry.disease.name}</h3>
                        <span class="${badgeClass}">${badgeText}</span>
                    </div>
                    <div class="mb-2">
                        <span class="fw-semibold d-block">Gejala terpenuhi</span>
                        <span>${formatSymptoms(entry.matched)}</span>
                    </div>
                    <div>
                        <span class="fw-semibold d-block">Perlu diperiksa</span>
                        <span>${entry.missing.length ? formatSymptoms(entry.missing) : 'Tidak ada'}</span>
                    </div>
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
