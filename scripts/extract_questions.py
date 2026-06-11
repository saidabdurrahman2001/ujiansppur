"""Ekstrak soal dari PDF Bahan Soal dan generate data/questions.json."""
import json
import os
import re
import hashlib
import pdfplumber

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAHAN_SOAL = os.path.join(ROOT, "Bahan Soal")
OUTPUT = os.path.join(ROOT, "data", "questions.json")

# Kunci jawaban & pembahasan (dari materi PUR & SP)
ANSWER_KEYS = {
    # PUR
    "pur_1": ("b", "Skema Kas Titipan bermitra dengan perbankan untuk memastikan ketersediaan uang tunai melalui layanan setoran, penarikan, dan penukaran uang di daerah berkebutuhan kas tinggi."),
    "pur_2": ("c", "Bantuan Pemeliharaan diberikan untuk memperpanjang umur, penambahan, dan pergantian sarana/prasarana yang rusak akibat usia dan pemakaian."),
    "pur_3": ("b", "Kolaborasi dengan mitra layanan (Pos, Pegadaian, BPR, PJPUR) memperluas kanal layanan dan meningkatkan efisiensi SDM serta infrastruktur."),
    "pur_4": ("c", "Pengembangan SI PUR dalam BPPUR 2024–2030 dikategorikan sebagai inisiatif strategis pada aspek Pengelolaan Uang Rupiah."),
    "pur_5": ("c", "DSCM adalah inisiatif integratif SMART (Seamless Integration, Modernization, Accountability, Resilience, Trustworthiness) untuk transformasi SI PUR."),
    "pur_6": ("c", "Outcome eksternal transformasi SI PUR adalah meningkatkan akuntabilitas dan kepercayaan masyarakat terhadap kebijakan PUR Bank Indonesia."),
    "pur_7": ("b", "Langkah awal Front Office: menahan uang (i), mencatat identitas nasabah (ii), dan memberi tanda terima (iv). Penyimpanan di brankas dilakukan setelahnya."),
    "pur_8": ("c", "Pihak selain bank/PJPUR wajib menjaga fisik uang, tidak mengedarkannya, dan meminta klarifikasi ke BI terdekat."),
    "pur_9": ("c", "Uang yang dinyatakan tidak asli diberi tanda khusus dan diserahkan ke Kepolisian Negara Republik Indonesia."),
    "pur_10": ("c", "Desain uang TE 2022 mempertahankan gambar pahlawan nasional dan tema budaya Indonesia."),
    "pur_11": ("b", "Watermark diseragamkan dengan gambar utama agar uang TE 2022 mudah dikenali masyarakat."),
    "pur_12": ("c", "Teknologi coating pada pecahan kecil (Rp1.000–Rp5.000) untuk memastikan masa edar uang yang lebih lama."),
    "pur_13": ("d", "PJPUR sebagai Sub Sirkulator mencakup pencetakan, distribusi, pengisian ATM/CDM, dan pembuatan ATM/CDM."),
    "pur_14": ("a", "Layar komputer menggunakan RGB, sedangkan mesin cetak menggunakan CMYK sehingga hasil cetak berbeda dari desain di layar."),
    "pur_15": ("b", "SPU SINERGI: identifikasi barcode (I), otomatisasi feeding & packaging (III), dan perekaman digital (IV). Proses tidak sepenuhnya manual."),
    # SP
    "sp_1": ("a", "Bank Indonesia memiliki wewenang tunggal mengajukan permohonan pailit terhadap PJP dan PIP."),
    "sp_2": ("b", "Rupiah Digital wholesale non-interest bearing karena fungsinya sebagai uang (alat pembayaran), dan uang tunai secara prinsip tidak membawa bunga."),
    "sp_3": ("d", "MDR ditanggung oleh Merchant/Pedagang sebagai biaya layanan infrastruktur, sesuai azas manfaat bagi merchant."),
    "sp_4": ("d", "Payment ID menjamin keamanan ekosistem melalui pembentukan profil risiko dan integritas transaksi SP."),
    "sp_5": ("b", "BI-Payment Clear mencegah transaksi mencurigakan melalui Fraudster Database dan watchlist terintegrasi pada tahap on-transaction."),
    "sp_6": ("b", "Digitalisasi UMKM memperluas ekosistem ekonomi digital hingga lapisan terbawah, mendukung inklusi keuangan."),
    "sp_7": ("a", "Langkah investigasi awal: isolasi infrastruktur terdampak dan audit forensik."),
    "sp_8": ("a", "Fast Payment (BIS/CPMI 2016): transmisi pesan dan ketersediaan dana secara real-time/near real-time, operasi 24/7."),
    "sp_9": ("c", "Pengawasan tidak langsung dilakukan melalui monitoring rutin data operasional harian dan laporan berkala."),
    "sp_10": ("a", "Perluasan QRIS TAP tepat: UMKM ritel NFC/Soundbox, angkutan daerah tap-on-bus, dan parkir berbasis gate. E-commerce mancanegara bukan prioritas."),
    "sp_11": ("a", "Target QRIS Antarnegara: titik kedatangan wisatawan, moda transportasi antarnegara, dan kawasan destinasi wisata."),
    "sp_12": ("d", "BI-ETP TIDAK digunakan untuk transaksi antar rekening masyarakat di bank — itu di luar ruang lingkup FMI BI."),
    "sp_13": ("d", "Siklus pengawasan SP: Pengawasan Tidak Langsung → Pemeriksaan → Tindak Lanjut."),
    "sp_14": ("d", "Penggunaan Uang Rupiah bukan substansi pengaturan Industri SP — itu domain PUR, bukan regulasi SP."),
    "sp_15": ("c", "Daerah terbatas infrastruktur/akseptasi digital: strategi QRIS Statis untuk sektor mikro (iv) paling tepat."),
}

PCPM_QUESTIONS = [
    {
        "id": "pcpm_1",
        "category": "PCPM",
        "source": "PCPM40 - KPw Advisor Ekonomi Daerah",
        "question": "Evolusi Tim Pengendalian Inflasi di Indonesia dimulai dari TPI (2005), kemudian berkembang menjadi TPID (2008). Berapa jumlah TPID yang mencakup seluruh Indonesia saat ini?",
        "options": {"a": "342 TPID", "b": "442 TPID", "c": "542 TPID", "d": "642 TPID"},
        "answer": "c",
        "explanation": "Materi PCPM menyebutkan evolusi TPI → TPID → Pokjanas → Keppres 23/2017 (TPIN), kini mencakup 542 TPID di seluruh Indonesia.",
    },
    {
        "id": "pcpm_2",
        "category": "PCPM",
        "source": "PCPM40 - KPw Advisor Ekonomi Daerah",
        "question": "Berapa persen inflasi nasional yang berasal dari daerah menurut materi pengendalian inflasi?",
        "options": {"a": "±60%", "b": "±70%", "c": "±80%", "d": "±90%"},
        "answer": "c",
        "explanation": "Sekitar ±80% inflasi nasional berasal dari daerah, sehingga pengendalian inflasi memerlukan peran aktif pemda melalui TPID.",
    },
    {
        "id": "pcpm_3",
        "category": "PCPM",
        "source": "PCPM40 - KPw Advisor Ekonomi Daerah",
        "question": "Payung hukum utama pengendalian inflasi berlandaskan pada peraturan berikut, KECUALI:",
        "options": {
            "a": "Keppres 23/2017",
            "b": "Permenko 10/2017",
            "c": "Peraturan sektoral 4K (Perpres, Permendag, Permentan, PP)",
            "d": "UU No. 23 Tahun 1999 tentang Bank Indonesia",
        },
        "answer": "d",
        "explanation": "Landasan hukum TPIP-TPID berlapis: Keppres 23/2017, Permenko 10/2017, dan regulasi sektoral 4K. UU BI bukan payung hukum langsung TPID.",
    },
    {
        "id": "pcpm_4",
        "category": "PCPM",
        "source": "PCPM40 - KPw Advisor Ekonomi Daerah",
        "question": "Struktur koordinasi pengendalian inflasi berjenjang dari pusat ke daerah adalah:",
        "options": {
            "a": "TPIN (Menko Perekonomian) → TPID Provinsi (Gubernur) → TPID Kab/Kota (Bupati/Walikota)",
            "b": "BI Pusat → KPwDN → TPID Provinsi → TPID Kab/Kota",
            "c": "Menko Perekonomian → Bupati/Walikota → Gubernur",
            "d": "TPIN → TPID Kab/Kota → TPID Provinsi",
        },
        "answer": "a",
        "explanation": "Struktur berjenjang: TPIN di pusat (Menko Perekonomian), TPID Provinsi (Gubernur), dan TPID Kab/Kota (Bupati/Walikota) dengan pelaporan dua arah.",
    },
    {
        "id": "pcpm_5",
        "category": "PCPM",
        "source": "PCPM40 - KPw Advisor Ekonomi Daerah",
        "question": "Siklus respons pengendalian inflasi yang dijalankan melalui forum rakor strategi 4K disebut:",
        "options": {"a": "SMART", "b": "PIKKE", "c": "DSCM", "d": "KEKDA"},
        "answer": "b",
        "explanation": "PIKKE = Pemantauan – Identifikasi – Koordinasi – Kebijakan – Evaluasi, dijalankan lewat 6 forum rakor strategi 4K.",
    },
    {
        "id": "pcpm_6",
        "category": "PCPM",
        "source": "PCPM40 - KPw Advisor Ekonomi Daerah",
        "question": "GNPIP (Gerakan Nasional Pengendalian Inflasi Pangan) diluncurkan pada 10 Agustus 2022 di kota:",
        "options": {"a": "Jakarta", "b": "Surabaya", "c": "Malang", "d": "Bandung"},
        "answer": "c",
        "explanation": "GNPIP diluncurkan 10 Agustus 2022 di Malang sebagai respons lonjakan inflasi volatile food 11,47%.",
    },
    {
        "id": "pcpm_7",
        "category": "PCPM",
        "source": "PCPM40 - KPw Advisor Ekonomi Daerah",
        "question": "Berapa tingkat inflasi volatile food saat peluncuran GNPIP yang menjadi latar belakang urgensi program tersebut?",
        "options": {"a": "8,47%", "b": "9,47%", "c": "10,47%", "d": "11,47%"},
        "answer": "d",
        "explanation": "GNPIP diluncurkan akibat lonjakan inflasi volatile food mencapai 11,47% pada saat itu.",
    },
    {
        "id": "pcpm_8",
        "category": "PCPM",
        "source": "PCPM40 - KPw Advisor Ekonomi Daerah",
        "question": "Program GNPIP yang kini diperkuat menjadi GPIPS (Gerakan Pengendalian Inflasi dan Pangan Sejahtera) diperbarui pada:",
        "options": {"a": "Mei 2024", "b": "Mei 2025", "c": "Mei 2026", "d": "Agustus 2026"},
        "answer": "c",
        "explanation": "GPIPS merupakan penguatan GNPIP untuk tantangan ketahanan pangan yang lebih kompleks, diperbarui Mei 2026.",
    },
    {
        "id": "pcpm_9",
        "category": "PCPM",
        "source": "PCPM40 - KPw Advisor Ekonomi Daerah",
        "question": "Strategi 4K dalam pengendalian inflasi mencakup, KECUALI:",
        "options": {
            "a": "Keterjangkauan",
            "b": "Ketersediaan",
            "c": "Kelancaran",
            "d": "Kemandirian",
        },
        "answer": "d",
        "explanation": "Strategi 4K: Keterjangkauan, Ketersediaan, Kelancaran, dan Komunikasi — bukan Kemandirian.",
    },
    {
        "id": "pcpm_10",
        "category": "PCPM",
        "source": "PCPM40 - KPw Advisor Ekonomi Daerah",
        "question": "Peran KPwDN dalam sinergi TPIP/TPID dapat mencakup fasilitasi operasi pasar melalui:",
        "options": {
            "a": "Penetapan suku bunga acuan daerah",
            "b": "Sewa tenda, meja, pemberian FDP, dan disinergikan dengan program kerja KPwDN",
            "c": "Pencetakan uang rupiah di daerah",
            "d": "Pengelolaan rekening kas umum daerah",
        },
        "answer": "b",
        "explanation": "KPwDN mendukung operasi pasar melalui fasilitasi penyelenggaraan (sewa tenda, meja), pemberian FDP, dan sinergi program kerja dengan timing/lokasi tepat sasaran.",
    },
]


def normalize_text(text: str) -> str:
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_abc_questions(text: str, category: str, source: str, prefix: str) -> list:
  """Parse soal format a/b/c/d."""
  text = re.sub(r"\n(?=[a-d]\.\s)", " ", text)
  blocks = re.split(r"(?=\d+\.\s)", text)
  questions = []

  for block in blocks:
    block = block.strip()
    m = re.match(r"(\d+)\.\s*(.+)", block, re.DOTALL)
    if not m:
      continue
    num = int(m.group(1))
    rest = m.group(2)

    opt_pattern = r"(?:^|\s)([a-d])\.\s+"
    parts = re.split(opt_pattern, rest)
    if len(parts) < 3:
      continue

    question_text = normalize_text(parts[0])
    options = {}
    for i in range(1, len(parts), 2):
      if i + 1 < len(parts):
        key = parts[i].lower()
        val = normalize_text(parts[i + 1])
        if key in "abcd":
          options[key] = val

    if len(options) < 4:
      continue

    qid = f"{prefix}_{num}"
    answer, explanation = ANSWER_KEYS.get(qid, ("a", "Jawaban berdasarkan materi Bank Indonesia."))

    questions.append({
      "id": qid,
      "category": category,
      "source": source,
      "question": question_text,
      "options": options,
      "answer": answer,
      "explanation": explanation,
    })

  return questions


def parse_bullet_questions(text: str, category: str, source: str, prefix: str) -> list:
  """Parse soal format bullet (●)."""
  text = text.replace("●", "\n● ")
  blocks = re.split(r"(?=\d+\.\s)", text)
  questions = []

  for block in blocks:
    block = block.strip()
    m = re.match(r"(\d+)\.\s*(.+)", block, re.DOTALL)
    if not m:
      continue
    num = int(m.group(1))
    rest = m.group(2)

    parts = re.split(r"\n●\s+", rest)
    question_text = normalize_text(parts[0])
    options = {}
    labels = ["a", "b", "c", "d"]
    for i, part in enumerate(parts[1:5]):
      options[labels[i]] = normalize_text(part)

    if len(options) < 4:
      continue

    qid = f"{prefix}_{num}"
    answer, explanation = ANSWER_KEYS.get(qid, ("a", "Jawaban berdasarkan materi Bank Indonesia."))

    questions.append({
      "id": qid,
      "category": category,
      "source": source,
      "question": question_text,
      "options": options,
      "answer": answer,
      "explanation": explanation,
    })

  return questions


def deduplicate(questions: list) -> list:
  seen = set()
  result = []
  for q in questions:
    h = hashlib.md5(q["question"].encode()).hexdigest()
    if h not in seen:
      seen.add(h)
      result.append(q)
  return result


def main():
  all_questions = []

  pdf_sources = [
    ("PUR.pdf", "PUR", "pur", parse_abc_questions),
    ("SP.pdf", "SP", "sp", parse_abc_questions),
    ("Latihan Soal SP PUR_Jawab.pdf", "SP", "sp", parse_bullet_questions),
  ]

  for filename, category, prefix, parser in pdf_sources:
    path = os.path.join(BAHAN_SOAL, filename)
    if not os.path.exists(path):
      continue
    with pdfplumber.open(path) as pdf:
      text = "\n".join((p.extract_text() or "") for p in pdf.pages)
    parsed = parser(text, category, filename, prefix)
    all_questions.extend(parsed)

  all_questions.extend(PCPM_QUESTIONS)
  all_questions = deduplicate(all_questions)

  os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
  payload = {
    "title": "Kuis SP & PUR - PCPM 40",
    "version": "1.0",
    "total": len(all_questions),
    "categories": ["PUR", "SP", "PCPM", "Semua"],
    "questions": all_questions,
  }

  with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

  js_output = os.path.join(ROOT, "js", "questions.js")
  os.makedirs(os.path.dirname(js_output), exist_ok=True)
  with open(js_output, "w", encoding="utf-8") as f:
    f.write("const QUIZ_DATA = ")
    json.dump(payload, f, ensure_ascii=False, indent=2)
    f.write(";\n")

  print(f"Generated {len(all_questions)} questions -> {OUTPUT}")


if __name__ == "__main__":
  main()
