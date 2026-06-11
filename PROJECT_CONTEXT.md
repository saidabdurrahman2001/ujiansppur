# PROJECT CONTEXT — Kuis SP & PUR (PCPM 40)

> **Dokumen referensi untuk AI/agent.** Baca file ini dulu sebelum mengubah atau menjawab pertanyaan tentang proyek ini, agar tidak perlu re-scan seluruh codebase.

**Workspace:** `c:\Users\Aman\Documents\Ngoding\2026-06-11-ujiansppur`  
**Dibuat:** Juni 2026  
**Bahasa UI:** Indonesia

---

## 1. Ringkasan Proyek

Aplikasi **kuis latihan berbasis web** (vanilla HTML/CSS/JS, tanpa framework) untuk materi:
- **PUR** — Pengelolaan Uang Rupiah (Bank Indonesia) — dari PDF `Bahan Soal/`
- **SP** — Sistem Pembayaran (Bank Indonesia) — dari PDF `Bahan Soal/`
- **20 paket Bahan Soal 2** — dari file `.txt` di `Bahan Soal 2/` (kategori = nama file, mis. `1. Soal Sistem Pembayaran` … `20. Catatan Kas Titipan`)

> **Dikecualikan (hanya PDF lama):** soal DR (`sp_2`) dari PDF — paket `ba2_*` tidak difilter.

Soal diambil dari PDF di folder `Bahan Soal/`, dikonversi ke JSON via script Python, lalu diload browser lewat `js/questions.js`.

### Fitur utama
| Fitur | Implementasi |
|-------|-------------|
| Kuis per kategori | `PUR`, `SP`, 20 paket `Bahan Soal 2`, `Semua` (23 kategori) |
| Acak soal | Checkbox `randomize`, Fisher-Yates shuffle di `app.js` |
| Nilai & grade | Skor % = `benar/total × 100`; grade di `getGrade()` |
| Pembahasan | Field `explanation` per soal, tampil setelah submit jawaban |
| Cache | `localStorage` key `kuis_sppur_cache_v1` |

---

## 2. Peta File (file mana untuk apa)

```
ujiansppur/
├── Bahan Soal/                    # PDF sumber (READ-ONLY saat runtime)
│   ├── PUR.pdf                    # 15 soal PUR (format a/b/c/d)
│   ├── SP.pdf                     # 15 soal SP (format a/b/c/d)
│   ├── SPPUR.pdf                  # Duplikat PUR (tidak dipakai extractor)
│   ├── Latihan Soal PUR_Jawab.pdf # Duplikat PUR, tanpa kunci terpisah
│   ├── Latihan Soal SP PUR_Jawab.pdf # 15 soal SP (format bullet ●)
│   └── PCPM40_*.pdf               # Slide presentasi (31 hal), BUKAN soal pilihan ganda
│
├── index.html                     # Entry point, 3 screen: home / quiz / result
├── css/style.css                  # Styling (tema BI biru #003d79, emas #c9a227)
├── js/
│   ├── questions.js               # const QUIZ_DATA = {...} — data soal untuk browser
│   └── app.js                     # Semua logika kuis, cache, navigasi
├── data/questions.json            # Mirror JSON (sumber edit + output script)
├── scripts/extract_questions.py     # Parser PDF → JSON + questions.js
├── README.md                      # Panduan singkat user
└── PROJECT_CONTEXT.md             # File ini (referensi agent)
```

### File yang paling sering disentuh
| Tugas | File |
|-------|------|
| Tambah/edit kunci jawaban PUR/SP | `scripts/extract_questions.py` → dict `ANSWER_KEYS` |
| Tambah soal PCPM manual | `scripts/extract_questions.py` → list `PCPM_QUESTIONS` |
| Ubah logika kuis/nilai/cache | `js/app.js` |
| Ubah tampilan | `css/style.css`, `index.html` |
| Regenerasi data soal | `python scripts/extract_questions.py` |

---

## 3. Arsitektur & Alur Data

```
PDF (Bahan Soal/)
    ↓  extract_questions.py
data/questions.json  +  js/questions.js (QUIZ_DATA)
    ↓  <script> di index.html
app.js membaca QUIZ_DATA, render UI, simpan localStorage
```

- **Tidak ada backend.** Bisa dibuka langsung `index.html` (file://) karena data di-embed di `questions.js`, bukan fetch JSON.
- **Tidak ada build step.** Edit → refresh browser.

---

## 4. Skema Data Soal

Setiap item di `QUIZ_DATA.questions`:

```json
{
  "id": "pur_1",
  "category": "PUR",
  "source": "PUR.pdf",
  "question": "Teks pertanyaan...",
  "options": { "a": "...", "b": "...", "c": "...", "d": "..." },
  "answer": "b",
  "explanation": "Pembahasan singkat..."
}
```

**ID convention:** `{prefix}_{nomor}` — `pur_1`…`pur_15`, `sp_1`…`sp_15`, `pcpm_1`…`pcpm_10`

**Kategori valid:** `PUR`, `SP`, `PCPM`, `Semua` (Semua = gabungan, bukan kategori soal)

---

## 5. Kunci Jawaban Resmi (ANSWER_KEYS)

Kunci jawaban PUR & SP didefinisikan di `scripts/extract_questions.py` → `ANSWER_KEYS`.  
PDF `_Jawab` **tidak memuat kunci terpisah**; kunci disusun manual dari materi.

### PUR (pur_1 – pur_15)
| ID | Jawaban |
|----|---------|
| pur_1 | b |
| pur_2 | c |
| pur_3 | b |
| pur_4 | c |
| pur_5 | c |
| pur_6 | c |
| pur_7 | b |
| pur_8 | c |
| pur_9 | c |
| pur_10 | c |
| pur_11 | b |
| pur_12 | c |
| pur_13 | d |
| pur_14 | a |
| pur_15 | b |

### SP (sp_1 – sp_15)
| ID | Jawaban |
|----|---------|
| sp_1 | a |
| sp_2 | b |
| sp_3 | d |
| sp_4 | d |
| sp_5 | b |
| sp_6 | b |
| sp_7 | a |
| sp_8 | a |
| sp_9 | c |
| sp_10 | a |
| sp_11 | a |
| sp_12 | d |
| sp_13 | d |
| sp_14 | d |
| sp_15 | c |

### PCPM (pcpm_1 – pcpm_10)
| ID | Jawaban | Topik singkat |
|----|---------|---------------|
| pcpm_1 | c | 542 TPID |
| pcpm_2 | c | ±80% inflasi dari daerah |
| pcpm_3 | d | Bukan UU BI sebagai payung TPID |
| pcpm_4 | a | TPIN → TPID Prov → TPID Kab/Kota |
| pcpm_5 | b | Siklus PIKKE |
| pcpm_6 | c | GNPIP diluncurkan Malang |
| pcpm_7 | d | Inflasi volatile food 11,47% |
| pcpm_8 | c | GPIPS Mei 2026 |
| pcpm_9 | d | 4K bukan Kemandirian |
| pcpm_10 | b | KPwDN fasilitasi operasi pasar |

---

## 6. Skema Cache (localStorage)

**Key:** `kuis_sppur_cache_v1`

```json
{
  "history": [
    {
      "date": "11/6/2026, 14.30.00",
      "category": "Semua",
      "score": 85,
      "correct": 34,
      "total": 40
    }
  ],
  "settings": {
    "category": "PUR",
    "randomize": true
  },
  "inProgress": {
    "category": "SP",
    "randomize": true,
    "questions": ["sp_3", "sp_7", "..."],
    "currentIndex": 2,
    "answers": { "sp_3": "b" },
    "submitted": { "sp_3": true }
  }
}
```

- `history`: max 50 entri (slice di `finishQuiz`)
- `inProgress`: `null` jika tidak ada kuis aktif; resume via banner "Lanjutkan Kuis"
- Hapus cache: tombol "Hapus Cache" → `localStorage.removeItem(CACHE_KEY)`

---

## 7. UI Screens & Elemen DOM

| Screen ID | Fungsi |
|-----------|--------|
| `screen-home` | Pilih kategori, jumlah soal, random, riwayat, mulai/resume |
| `screen-quiz` | Soal aktif, pilihan, pembahasan, submit/next |
| `screen-result` | Skor, grade, ringkasan benar/salah |

**Tombol penting:** `btn-start`, `btn-resume`, `btn-submit`, `btn-next`, `btn-quit`, `btn-home`, `btn-retry`, `btn-clear-cache`

**State runtime** (`app.js` → `state` object):
```js
{ category, randomize, questionCount, questions[], currentIndex, answers{}, submitted{}, finished }
```

---

## 8. Sistem Penilaian

```js
score = Math.round((correct / total) * 100)
```

| Skor | Grade |
|------|-------|
| ≥ 90 | Sangat Baik 🏆 |
| ≥ 80 | Baik ⭐ |
| ≥ 70 | Cukup 👍 |
| ≥ 60 | Kurang 📚 |
| < 60 | Perlu Belajar Lagi 💪 |

Fungsi: `getGrade(score)` di `js/app.js`

---

## 9. Parser PDF (`extract_questions.py`)

### Sumber yang diparsing
| File PDF | Parser | Prefix |
|----------|--------|--------|
| `PUR.pdf` | `parse_abc_questions` | pur |
| `SP.pdf` | `parse_abc_questions` | sp |
| `Latihan Soal SP PUR_Jawab.pdf` | `parse_bullet_questions` (●) | sp |

### Tidak diparsing
- `SPPUR.pdf`, `Latihan Soal PUR_Jawab.pdf` — duplikat, di-dedup by hash pertanyaan
- `PCPM40_*.pdf` — slide, soal dibuat manual di `PCPM_QUESTIONS`

### Regenerasi data
```bash
cd c:\Users\Aman\Documents\Ngoding\2026-06-11-ujiansppur
python scripts/extract_questions.py
```
Output: `data/questions.json` + `js/questions.js`

### Known issue parser ⚠️
Regex split `(?=\d+\.\s)` kadang salah pada soal **PUR no. 10–15** (nomor soal bentrok dengan angka di teks, mis. "2022"). Gejala di `questions.json`:
- ID duplikat (`pur_0`, `pur_1` muncul 2×)
- `answer` / `explanation` tidak match pertanyaan (fallback `ANSWER_KEYS` salah key)

**Perbaikan:** perbaiki regex di `parse_abc_questions`, atau assign ID by sequence bukan by nomor di PDF, lalu re-run script.

---

## 10. Cara Menjalankan

```bash
# Opsi 1: buka langsung
start index.html

# Opsi 2: HTTP server
python -m http.server 8080
# → http://localhost:8080
```

Dependency Python (hanya untuk extract): `pdfplumber`, `pypdf`

---

## 11. Panduan Modifikasi Cepat

### Tambah soal baru dari PDF
1. Letakkan PDF di `Bahan Soal/`
2. Tambah entry di `pdf_sources` list di `extract_questions.py`
3. Tambah kunci di `ANSWER_KEYS` atau buat list manual seperti `PCPM_QUESTIONS`
4. Run `python scripts/extract_questions.py`

### Ubah grade threshold
Edit `getGrade()` di `js/app.js`

### Ubah tema warna
Edit CSS variables di `css/style.css` → `:root`

### Tambah fitur (timer, export, dll)
- Logika → `js/app.js`
- UI → `index.html` + `css/style.css`
- Persist → extend schema cache di `loadCache`/`saveCache`

### Fix jawaban salah
1. Edit `ANSWER_KEYS` di `extract_questions.py` (PUR/SP)
2. Atau edit langsung `data/questions.json` lalu copy ke `js/questions.js` (wrap: `const QUIZ_DATA = ...;`)
3. Prefer: fix script + re-run agar konsisten

---

## 12. Konteks Bahan Soal PDF

| File | Isi | Dipakai? |
|------|-----|----------|
| `PUR.pdf` | 15 MCQ PUR | ✅ |
| `SP.pdf` | 15 MCQ SP | ✅ |
| `Latihan Soal SP PUR_Jawab.pdf` | 15 MCQ SP (format ●) | ✅ (dedup dengan SP.pdf) |
| `Latihan Soal PUR_Jawab.pdf` | 15 MCQ PUR | ❌ duplikat PUR.pdf |
| `SPPUR.pdf` | 15 MCQ PUR | ❌ duplikat |
| `PCPM40_*.pdf` | Slide KPw advisor ekonomi daerah | ✅ → 10 soal manual |

Topik PCPM slide: KEKDA, KPwDN koordinator, TPID/TPIN, strategi 4K, PIKKE, GNPIP→GPIPS, peran KPw Kalsel.

---

## 13. Statistik Saat Ini

- **Total soal unik:** ~628 (15 PUR + 15 SP PDF + ~598 dari 20 paket Bahan Soal 2)
- **Regenerasi:** `python scripts/extract_questions.py` — parser Bahan Soal 2: `parse_bahan_soal2_txt()`
- **Tech:** HTML5, CSS3, vanilla JS, Python 3 + pdfplumber
- **Git:** workspace di `Documents/Ngoding/2026-06-11-ujiansppur`

---

## 14. Instruksi untuk Agent/AI

Saat user bertanya tentang proyek ini:
1. **Baca `PROJECT_CONTEXT.md` ini terlebih dahulu**
2. Untuk detail soal spesifik → `data/questions.json` atau `ANSWER_KEYS`
3. Untuk bug UI/logika → `js/app.js`
4. Untuk styling → `css/style.css`
5. Jangan scan ulang folder `Bahan Soal/` kecuali user minta update dari PDF
6. Setelah edit `extract_questions.py`, selalu jalankan ulang script untuk sync `questions.js`
