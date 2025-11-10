# Sistem Diagnosa Penyakit Sapi Madura (Forward Chaining)

Layanan REST berbasis FastAPI dengan UI web ringan untuk mendiagnosis penyakit sapi menggunakan gejala biner dan mesin inferensi forward chaining.

## Persiapan Lingkungan

1. Gunakan Python 3.11.
2. Pasang dependensi:
   ```bash
   pip install -r requirements.txt
   ```

## Menjalankan Aplikasi

```bash
uvicorn app.main:app --reload
```

Akses UI pada `http://localhost:8000/` untuk memilih gejala dan melihat hasil diagnosa.

## API Utama

- `GET /api/symptoms` – daftar gejala dari knowledge base.
- `POST /api/diagnose?strict=true|false` – kirim payload berikut:
  ```json
  {
    "selected": ["JG01", "JG02", "JG03", "JG04"]
  }
  ```
  `strict=true` hanya menampilkan rule lengkap, sedangkan `strict=false` (default) juga menampilkan kandidat parsial.

Contoh curl:
```bash
curl -X POST "http://localhost:8000/api/diagnose?strict=true" \
     -H "Content-Type: application/json" \
     -d '{"selected":["JG01","JG02","JG03","JG04"]}'
```

## Pengujian

Jalankan semua tes pytest:
```bash
pytest
```

## Docker

```bash
docker build -t diagnosa-sapi .
docker run -p 8000:8000 diagnosa-sapi
```