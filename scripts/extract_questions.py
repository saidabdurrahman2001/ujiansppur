"""Ekstrak soal dari PDF Bahan Soal dan generate data/questions.json."""
import json
import os
import re
import hashlib
import pdfplumber

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAHAN_SOAL = os.path.join(ROOT, "Bahan Soal")
BAHAN_SOAL_2 = os.path.join(ROOT, "Bahan Soal 2")
OUTPUT = os.path.join(ROOT, "data", "questions.json")

# Kunci jawaban & pembahasan (dari materi PUR & SP)
ANSWER_KEYS = {
    # PUR
    "pur_1": ("b", "Skema Kas Titipan bermitra dengan perbankan untuk memastikan ketersediaan uang tunai melalui layanan setoran, penarikan, dan penukaran uang di daerah berkebutuhan kas tinggi."),
    "pur_2": ("c", "Bantuan Pemeliharaan diberikan untuk memperpanjang umur, penambahan, dan pergantian sarana/prasarana yang rusak akibat usia dan pemakaian."),
    "pur_3": ("b", "Kolaborasi dengan mitra layanan (Pos, Pegadaian, BPR, PJPUR) memperluas kanal layanan dan meningkatkan efisiensi SDM serta infrastruktur."),
    "pur_4": ("d", "Pengembangan SI PUR dalam BPPUR 2024–2030 dikategorikan sebagai inisiatif strategis pada aspek Infrastruktur PUR."),
    "pur_5": ("c", "DSCM adalah inisiatif integratif SMART (Seamless Integration, Modernization, Accountability, Resilience, Trustworthiness) untuk transformasi SI PUR."),
    "pur_6": ("c", "Outcome eksternal transformasi SI PUR adalah meningkatkan akuntabilitas dan kepercayaan masyarakat terhadap kebijakan PUR Bank Indonesia."),
    "pur_7": ("b", "Langkah awal Front Office: menahan uang (i), mencatat identitas nasabah (ii), dan memberi tanda terima (iv). Penyimpanan di brankas dilakukan setelahnya."),
    "pur_8": ("c", "Pihak selain bank/PJPUR wajib menjaga fisik uang, tidak mengedarkannya, dan meminta klarifikasi ke BI terdekat."),
    "pur_9": ("c", "Uang yang dinyatakan tidak asli diberi tanda khusus dan diserahkan ke Kepolisian Negara Republik Indonesia."),
    "pur_10": ("c", "Desain uang TE 2022 mempertahankan gambar pahlawan nasional dan tema budaya Indonesia."),
    "pur_11": ("b", "Watermark diseragamkan dengan gambar utama agar uang TE 2022 mudah dikenali masyarakat."),
    "pur_12": ("c", "Teknologi coating pada pecahan kecil (Rp1.000–Rp5.000) untuk memastikan masa edar uang yang lebih lama."),
    "pur_13": ("c", "Ruang lingkup PJPUR yang benar adalah Distribusi Uang (II) dan Pengisian ATM/CDM (III)."),
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

# Soal yang dikecualikan: materi KPw/PCPM lama
EXCLUDED_IDS = set()
EXCLUDED_KEYWORDS = (
    "KPw",
    "KPW",
    "KPwDN",
    "pcpm_",
)


def is_excluded(question: dict) -> bool:
    if question.get("id", "").startswith("ba2_"):
        return False
    if question.get("id") in EXCLUDED_IDS:
        return True
    if question.get("id", "").startswith("pcpm_"):
        return True
    text = question.get("question", "") + " " + question.get("source", "")
    return any(kw in text for kw in EXCLUDED_KEYWORDS)


def normalize_text(text: str) -> str:
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def format_list_in_question(text: str) -> str:
    """Pisahkan item I/II/III/IV atau (i)/(ii)/(iii)/(iv) ke baris baru agar mudah dibaca."""
    text = re.sub(r"\s+((?:I{1,3}|IV))\.\s+", r"\n\1. ", text)
    text = re.sub(r"\s+([iv])\.\s+", r"\n\1. ", text)
    text = re.sub(r"\s+\(([ivx]+)\)\s+", r"\n(\1) ", text, flags=re.I)
    return text.strip()


def question_fingerprint(question: str) -> str:
    """Fingerprint untuk deteksi soal duplikat/near-duplikat."""
    text = question.lower()
    text = re.sub(r"[^a-z0-9]", "", text)
    return text[:100]


def split_numbered_blocks(text: str) -> list[tuple[int, str]]:
    """Pecah teks soal berdasarkan nomor di awal baris (hindari split '10.' -> '0.')."""
    parts = re.split(r"(?:(?<=\n)|^)(\d{1,2})\.\s+", text)
    blocks = []
    idx = 1 if parts and not parts[0].strip() else 0

    if idx == 0:
        m = re.match(r"(\d{1,2})\.\s+([\s\S]*)", text.strip())
        if m:
            blocks.append((int(m.group(1)), m.group(2)))
        return blocks

    while idx < len(parts) - 1:
        blocks.append((int(parts[idx]), parts[idx + 1]))
        idx += 2
    return blocks


def parse_abc_questions(text: str, category: str, source: str, prefix: str) -> list:
  """Parse soal format a/b/c/d."""
  text = re.sub(r"\n(?=[a-d]\.\s)", " ", text)
  questions = []

  for num, rest in split_numbered_blocks(text):
    opt_pattern = r"(?:^|\s)([a-d])\.\s+"
    parts = re.split(opt_pattern, rest)
    if len(parts) < 3:
      continue

    question_text = format_list_in_question(normalize_text(parts[0]))
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
  questions = []

  for num, rest in split_numbered_blocks(text):
    rest = rest.strip()

    parts = re.split(r"\n●\s+", rest)
    question_text = format_list_in_question(normalize_text(parts[0]))
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


def parse_bahan_soal2_txt(text: str, category: str, source: str, prefix: str) -> list:
  """Parse paket soal dari file .txt di folder Bahan Soal 2."""
  text = text.replace("\r\n", "\n")
  text = re.sub(r"^.*?(?=Soal\s+\d+\s*:)", "", text, count=1, flags=re.I | re.DOTALL)

  blocks = re.split(r"(?=Soal\s+\d+\s*:)", text, flags=re.I)
  questions = []

  for block in blocks:
    block = block.strip().strip(",").strip()
    if not block:
      continue

    m = re.match(r"Soal\s+(\d+)\s*:\s*(.+)", block, re.I | re.DOTALL)
    if not m:
      continue
    num = int(m.group(1))
    rest = m.group(2)

    ans_m = re.search(r"Jawaban:\s*([A-Da-d])(?:\s*\(([^)]+)\))?", rest, re.I)
    if not ans_m:
      continue

    answer = ans_m.group(1).lower()
    explanation_extra = (ans_m.group(2) or "").strip()
    q_body = re.sub(r"\s+", " ", rest[: ans_m.start()].strip())

    opt_parts = re.split(r"\s+([A-D])\.\s+", q_body, flags=re.I)
    if len(opt_parts) < 2:
      continue

    question_text = format_list_in_question(normalize_text(opt_parts[0]))
    options = {}
    for i in range(1, len(opt_parts), 2):
      if i + 1 < len(opt_parts):
        key = opt_parts[i].lower()
        val = normalize_text(opt_parts[i + 1])
        if key in "abcd":
          options[key] = val

    if len(options) < 4:
      continue

    correct_text = options.get(answer, "")
    if explanation_extra:
      explanation = f"{explanation_extra}. Jawaban benar: {correct_text}"
    else:
      explanation = f"Jawaban benar ({answer.upper()}): {correct_text}"

    questions.append({
      "id": f"{prefix}_{num}",
      "category": category,
      "source": source,
      "question": question_text,
      "options": options,
      "answer": answer,
      "explanation": explanation,
    })

  return questions


def load_bahan_soal2_packages() -> tuple[list, list]:
  """Muat 20 paket soal dari Bahan Soal 2. Return (categories, questions)."""
  if not os.path.isdir(BAHAN_SOAL_2):
    return [], []

  txt_files = [
    f for f in os.listdir(BAHAN_SOAL_2)
    if f.lower().endswith(".txt")
  ]
  txt_files.sort(key=lambda name: int(m.group(1)) if (m := re.match(r"^(\d+)", name)) else 999)

  categories = []
  questions = []

  for fname in txt_files:
    num_m = re.match(r"^(\d+)", fname)
    pkg_num = int(num_m.group(1)) if num_m else len(categories) + 1
    category = os.path.splitext(fname)[0].strip()
    prefix = f"ba2_{pkg_num:02d}"
    path = os.path.join(BAHAN_SOAL_2, fname)

    with open(path, encoding="utf-8") as f:
      text = f.read()

    parsed = parse_bahan_soal2_txt(text, category, fname, prefix)
    if parsed:
      categories.append(category)
      questions.extend(parsed)

  return categories, questions


def deduplicate_by_id(questions: list) -> list:
  """Buang duplikat ID — penyebab jawaban auto-terisi di soal berikutnya."""
  by_id = {}
  for q in questions:
    by_id[q["id"]] = q
  return list(by_id.values())


def deduplicate(questions: list) -> list:
  """Buang soal berulang (teks sama atau fingerprint mirip)."""
  seen_exact = set()
  seen_fp = set()
  result = []
  for q in questions:
    exact = hashlib.md5(q["question"].encode()).hexdigest()
    fp = question_fingerprint(q["question"])
    if exact in seen_exact or fp in seen_fp:
      continue
    seen_exact.add(exact)
    seen_fp.add(fp)
    result.append(q)
  return result


def main():
  all_questions = []
  ba2_categories, ba2_questions = load_bahan_soal2_packages()

  pdf_sources = [
    ("PUR.pdf", "PUR", "pur", parse_abc_questions),
    ("SP.pdf", "SP", "sp", parse_abc_questions),
  ]

  for filename, category, prefix, parser in pdf_sources:
    path = os.path.join(BAHAN_SOAL, filename)
    if not os.path.exists(path):
      continue
    with pdfplumber.open(path) as pdf:
      text = "\n".join((p.extract_text() or "") for p in pdf.pages)
    parsed = parser(text, category, filename, prefix)
    all_questions.extend(parsed)

  all_questions.extend(ba2_questions)
  all_questions = deduplicate_by_id(all_questions)
  all_questions = deduplicate(all_questions)
  all_questions = [q for q in all_questions if not is_excluded(q)]

  base_categories = ["PUR", "SP"]
  categories = base_categories + [c for c in ba2_categories if c not in base_categories] + ["Semua"]

  os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
  payload = {
    "title": "Kuis SP & PUR",
    "version": "2.0",
    "total": len(all_questions),
    "categories": categories,
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

  print(f"Generated {len(all_questions)} questions ({len(ba2_categories)} paket Bahan Soal 2) -> {OUTPUT}")


if __name__ == "__main__":
  main()
