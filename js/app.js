const CACHE_KEY = "kuis_sppur_cache_v3";

const state = {
  category: "Semua",
  randomize: true,
  questionCount: 0,
  questions: [],
  currentIndex: 0,
  answers: {},
  submitted: {},
  finished: false,
};

function loadCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    return raw ? JSON.parse(raw) : { history: [], settings: {}, inProgress: null };
  } catch {
    return { history: [], settings: {}, inProgress: null };
  }
}

function saveCache(data) {
  localStorage.setItem(CACHE_KEY, JSON.stringify(data));
}

function getCategoryCount(cat) {
  if (cat === "Semua") return QUIZ_DATA.questions.length;
  return QUIZ_DATA.questions.filter((q) => q.category === cat).length;
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function getGrade(score) {
  if (score >= 90) return { label: "Sangat Baik", emoji: "🏆" };
  if (score >= 80) return { label: "Baik", emoji: "⭐" };
  if (score >= 70) return { label: "Cukup", emoji: "👍" };
  if (score >= 60) return { label: "Kurang", emoji: "📚" };
  return { label: "Perlu Belajar Lagi", emoji: "💪" };
}

function showScreen(id) {
  document.querySelectorAll(".screen").forEach((el) => el.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}

function initHome() {
  const cache = loadCache();
  const grid = document.getElementById("category-grid");
  grid.innerHTML = "";

  QUIZ_DATA.categories.forEach((cat) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "category-btn" + (state.category === cat ? " active" : "");
    btn.dataset.category = cat;
    btn.innerHTML = `${cat}<span class="count">${getCategoryCount(cat)} soal</span>`;
    btn.addEventListener("click", () => {
      state.category = cat;
      document.querySelectorAll(".category-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      updateQuestionCountMax();
    });
    grid.appendChild(btn);
  });

  const saved = cache.settings;
  if (saved.category) state.category = saved.category;
  if (saved.randomize !== undefined) state.randomize = saved.randomize;
  document.getElementById("randomize").checked = state.randomize;

  updateQuestionCountMax();
  renderHistory(cache.history);

  if (cache.inProgress) {
    document.getElementById("resume-banner").classList.remove("hidden");
    document.getElementById("resume-info").textContent =
      `Kuis ${cache.inProgress.category} — soal ${cache.inProgress.currentIndex + 1}/${cache.inProgress.questions.length}`;
  } else {
    document.getElementById("resume-banner").classList.add("hidden");
  }
}

function updateQuestionCountMax() {
  const max = getCategoryCount(state.category);
  const input = document.getElementById("question-count");
  input.max = max;
  if (!input.value || parseInt(input.value, 10) > max) {
    input.value = max;
  }
  state.questionCount = parseInt(input.value, 10);
}

function renderHistory(history) {
  const list = document.getElementById("history-list");
  if (!history.length) {
    list.innerHTML = '<li style="color:var(--muted)">Belum ada riwayat kuis</li>';
    return;
  }
  list.innerHTML = history
    .slice(0, 10)
    .map(
      (h) =>
        `<li><span>${h.date} — ${h.category}</span><span class="score-badge">${h.score}% (${h.correct}/${h.total})</span></li>`
    )
    .join("");
}

function questionFingerprint(text) {
  return (text || "")
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "")
    .slice(0, 100);
}

function dedupeQuestionPool(pool) {
  const seen = new Set();
  return pool.filter((q) => {
    const fp = questionFingerprint(q.question);
    if (seen.has(fp)) return false;
    seen.add(fp);
    return true;
  });
}

function prepareQuestions() {
  let pool =
    state.category === "Semua"
      ? [...QUIZ_DATA.questions]
      : QUIZ_DATA.questions.filter((q) => q.category === state.category);

  pool = dedupeQuestionPool(pool);
  if (state.randomize) pool = shuffle(pool);

  const count = Math.min(state.questionCount || pool.length, pool.length);
  return pool.slice(0, count);
}

function saveProgress() {
  const cache = loadCache();
  if (state.finished) {
    cache.inProgress = null;
  } else {
    cache.inProgress = {
      category: state.category,
      randomize: state.randomize,
      questions: state.questions.map((q) => q.id),
      currentIndex: state.currentIndex,
      answers: state.answers,
      submitted: state.submitted,
    };
  }
  cache.settings = { category: state.category, randomize: state.randomize };
  saveCache(cache);
}

function startQuiz(resume = false) {
  state.randomize = document.getElementById("randomize").checked;
  state.questionCount = parseInt(document.getElementById("question-count").value, 10);

  const cache = loadCache();

  if (resume && cache.inProgress) {
    const prog = cache.inProgress;
    state.category = prog.category;
    state.randomize = prog.randomize;
    state.questions = prog.questions
      .map((id) => QUIZ_DATA.questions.find((q) => q.id === id))
      .filter(Boolean);
    state.currentIndex = prog.currentIndex;
    state.answers = prog.answers || {};
    state.submitted = prog.submitted || {};
    state.finished = false;
  } else {
    state.questions = prepareQuestions();
    state.currentIndex = 0;
    state.answers = {};
    state.submitted = {};
    state.finished = false;
  }

  if (!state.questions.length) {
    alert("Tidak ada soal untuk kategori ini.");
    return;
  }

  saveProgress();
  showScreen("screen-quiz");
  renderQuestion();
}

function renderQuestion() {
  const q = state.questions[state.currentIndex];
  const total = state.questions.length;
  const pct = ((state.currentIndex + 1) / total) * 100;

  document.getElementById("quiz-progress-text").textContent =
    `Soal ${state.currentIndex + 1} dari ${total}`;
  document.getElementById("quiz-category").textContent = q.category;
  document.getElementById("progress-fill").style.width = `${pct}%`;
  document.getElementById("question-source").textContent = q.source;
  document.getElementById("question-text").textContent = q.question || "";

  const choicesEl = document.getElementById("choices");
  const pembahasanEl = document.getElementById("pembahasan");
  pembahasanEl.classList.add("hidden");
  choicesEl.innerHTML = "";

  const idx = state.currentIndex;
  const isSubmitted = state.submitted[idx];
  const userAnswer = state.answers[idx];

  Object.entries(q.options).forEach(([key, text]) => {
    const div = document.createElement("div");
    div.className = "choice";
    if (isSubmitted) div.classList.add("disabled");
    if (userAnswer === key) div.classList.add("selected");
    if (isSubmitted) {
      if (key === q.answer) div.classList.add("correct");
      else if (userAnswer === key) div.classList.add("wrong");
    }

    div.innerHTML = `<span class="choice-key">${key.toUpperCase()}</span><span class="choice-text">${text}</span>`;
    if (!isSubmitted) {
      div.addEventListener("click", () => selectAnswer(idx, key));
    }
    choicesEl.appendChild(div);
  });

  const btnSubmit = document.getElementById("btn-submit");
  const btnNext = document.getElementById("btn-next");

  if (isSubmitted) {
    btnSubmit.classList.add("hidden");
    btnNext.classList.remove("hidden");
    btnNext.textContent =
      state.currentIndex < total - 1 ? "Soal Berikutnya →" : "Lihat Hasil";

    pembahasanEl.classList.remove("hidden");
    const correctText = q.options[q.answer];
    const status =
      userAnswer === q.answer
        ? `<span style="color:var(--success)">✓ Benar</span>`
        : `<span style="color:var(--danger)">✗ Salah — Jawaban: ${q.answer.toUpperCase()}. ${correctText}</span>`;
    pembahasanEl.innerHTML = `<strong>Pembahasan:</strong> ${status}<br><br>${q.explanation}`;
  } else {
    btnSubmit.classList.remove("hidden");
    btnNext.classList.add("hidden");
    btnSubmit.disabled = !userAnswer;
  }

  saveProgress();
}

function selectAnswer(index, key) {
  state.answers[index] = key;
  document.getElementById("btn-submit").disabled = false;
  renderQuestion();
}

function submitAnswer() {
  const idx = state.currentIndex;
  if (!state.answers[idx]) return;
  state.submitted[idx] = true;
  renderQuestion();
}

function nextQuestion() {
  if (state.currentIndex < state.questions.length - 1) {
    state.currentIndex++;
    renderQuestion();
  } else {
    finishQuiz();
  }
}

function finishQuiz() {
  state.finished = true;
  const total = state.questions.length;
  let correct = 0;

  state.questions.forEach((q, i) => {
    if (state.answers[i] === q.answer) correct++;
  });

  const score = Math.round((correct / total) * 100);
  const grade = getGrade(score);

  const cache = loadCache();
  cache.history.unshift({
    date: new Date().toLocaleString("id-ID"),
    category: state.category,
    score,
    correct,
    total,
  });
  cache.history = cache.history.slice(0, 50);
  cache.inProgress = null;
  saveCache(cache);

  document.getElementById("score-value").textContent = score;
  document.getElementById("score-detail").textContent = `${correct} benar dari ${total} soal`;
  document.getElementById("grade-text").textContent = `${grade.emoji} ${grade.label}`;

  const review = document.getElementById("review-list");
  review.innerHTML = state.questions
    .map((q, i) => {
      const ok = state.answers[i] === q.answer;
      return `<div class="review-item">
        <div class="q-num">Soal ${i + 1} [${q.category}]</div>
        <div>${q.question.substring(0, 120)}${q.question.length > 120 ? "..." : ""}</div>
        <div class="status ${ok ? "correct" : "wrong"}">${ok ? "✓ Benar" : `✗ Salah (Jawaban: ${q.answer.toUpperCase()})`}</div>
      </div>`;
    })
    .join("");

  showScreen("screen-result");
}

function clearCache() {
  if (confirm("Hapus semua data cache (riwayat & progress)?")) {
    localStorage.removeItem(CACHE_KEY);
    initHome();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initHome();

  document.getElementById("question-count").addEventListener("change", updateQuestionCountMax);
  document.getElementById("btn-start").addEventListener("click", () => startQuiz(false));
  document.getElementById("btn-resume").addEventListener("click", () => startQuiz(true));
  document.getElementById("btn-submit").addEventListener("click", submitAnswer);
  document.getElementById("btn-next").addEventListener("click", nextQuestion);
  document.getElementById("btn-home").addEventListener("click", () => {
    initHome();
    showScreen("screen-home");
  });
  document.getElementById("btn-retry").addEventListener("click", () => {
    startQuiz(false);
  });
  document.getElementById("btn-clear-cache").addEventListener("click", clearCache);
  document.getElementById("btn-quit").addEventListener("click", () => {
    saveProgress();
    initHome();
    showScreen("screen-home");
  });
});
