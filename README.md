# Kuis SP & PUR — PCPM 40

Aplikasi kuis latihan berbasis web dari bahan soal folder `Bahan Soal`.

> **Referensi lengkap proyek:** lihat [`PROJECT_CONTEXT.md`](./PROJECT_CONTEXT.md) — berisi peta file, skema data, kunci jawaban, cache, dan panduan modifikasi untuk AI/developer.

## Fitur

- **31 soal** dari materi PUR (15) dan SP (14) — tanpa soal DR & KPW
- **Nilai otomatis** dengan grade (Sangat Baik / Baik / Cukup / dll)
- **Acak urutan soal** (opsional)
- **Pembahasan** setiap soal setelah menjawab
- **Cache localStorage** — menyimpan progress kuis & riwayat nilai

## Cara Menjalankan

Buka langsung di browser:

```
index.html
```

Atau jalankan server lokal:

```bash
python -m http.server 8080
```

Lalu buka `http://localhost:8080`

## Update Soal dari PDF

Jika ada perubahan di folder `Bahan Soal`, jalankan:

```bash
python scripts/extract_questions.py
```

Script akan memperbarui `data/questions.json` dan `js/questions.js`.

## Struktur

```
├── Bahan Soal/          # PDF sumber soal
├── data/questions.json  # Data soal (JSON)
├── js/
│   ├── questions.js     # Data soal (untuk browser)
│   └── app.js           # Logika kuis
├── css/style.css
├── index.html
└── scripts/extract_questions.py
```
