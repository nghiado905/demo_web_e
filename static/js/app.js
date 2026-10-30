/**
 * EnglishMaster Quiz Pro - Local Interactive Application Engine
 * Handles Practice Mode, Timed Exam Mode, Audio Speech, Mistakes Tracking, and Stats.
 */

class QuizApp {
  constructor() {
    this.soundEnabled = localStorage.getItem("quiz_sound") !== "false";
    this.theme = localStorage.getItem("quiz_theme") || "dark";
    
    // Core state
    this.sets = [];
    this.activeSet = null;
    this.activeMode = "exam"; // 'exam' | 'practice' | 'review'
    this.questions = [];
    this.currentIndex = 0;
    this.userAnswers = {}; // { q_id: option_index }
    this.flaggedQuestions = new Set();
    this.practiceRevealed = {}; // { q_id: true }
    
    // Timer state
    this.timerInterval = null;
    this.timeRemaining = 0;
    this.totalTimeSpent = 0;
    
    // Results
    this.lastExamResult = null;
    
    // Web Audio Context for synthesized sound effects
    this.audioCtx = null;

    this.init();
  }

  init() {
    this.applyTheme(this.theme);
    this.updateSoundIcon();
    this.loadStats();
    this.loadTestSets();
    this.setupKeyboardShortcuts();
  }

  /* ========================================================
     THEME & AUDIO SETTINGS
     ======================================================== */
  applyTheme(theme) {
    this.theme = theme;
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("quiz_theme", theme);
    const themeIcon = document.getElementById("themeIcon");
    if (themeIcon) {
      themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
    }
  }

  toggleTheme() {
    this.applyTheme(this.theme === "dark" ? "light" : "dark");
    this.showToast(`Đã chuyển sang chế độ ${this.theme === "dark" ? "Tối" : "Sáng"}`);
  }

  toggleSound() {
    this.soundEnabled = !this.soundEnabled;
    localStorage.setItem("quiz_sound", this.soundEnabled);
    this.updateSoundIcon();
    this.showToast(this.soundEnabled ? "Đã bật âm thanh hiệu ứng" : "Đã tắt âm thanh");
  }

  updateSoundIcon() {
    const icon = document.getElementById("soundIcon");
    if (icon) {
      icon.textContent = this.soundEnabled ? "🔊" : "🔇";
    }
  }

  playSound(type) {
    if (!this.soundEnabled) return;
    try {
      if (!this.audioCtx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.audioCtx = new AudioContext();
      }
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }

      const now = this.audioCtx.currentTime;
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);

      if (type === "correct") {
        // Melodic two-tone success chord
        osc.type = "sine";
        osc.frequency.setValueAtTime(587.33, now); // D5
        osc.frequency.setValueAtTime(880.00, now + 0.1); // A5
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
        osc.start(now);
        osc.stop(now + 0.35);
      } else if (type === "wrong") {
        // Low buzzy error chord
        osc.type = "triangle";
        osc.frequency.setValueAtTime(196, now); // G3
        osc.frequency.setValueAtTime(174, now + 0.1); // F3
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
        osc.start(now);
        osc.stop(now + 0.3);
      } else if (type === "click") {
        // Subtle click
        osc.type = "sine";
        osc.frequency.setValueAtTime(700, now);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
        osc.start(now);
        osc.stop(now + 0.08);
      }
    } catch (e) {
      console.warn("Audio error:", e);
    }
  }

  speakText(text) {
    if (!('speechSynthesis' in window)) {
      this.showToast("Trình duyệt không hỗ trợ phát âm Web Speech API");
      return;
    }
    window.speechSynthesis.cancel(); // Stop prior audio
    const cleanText = text.replace(/______/g, "blank").replace(/[_]{2,}/g, "blank");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = "en-US";
    utterance.rate = 0.92; // Slightly clear and natural pace for learners
    
    // Pick an English voice if available
    const voices = window.speechSynthesis.getVoices();
    const enVoice = voices.find(v => v.lang.startsWith("en-US") || v.lang.startsWith("en-GB"));
    if (enVoice) utterance.voice = enVoice;

    const btn = document.getElementById("btnPlayAudio");
    if (btn) btn.innerHTML = "<span>🔊</span> Đang đọc...";

    utterance.onend = () => {
      if (btn) btn.innerHTML = "<span>🔊</span> Nghe Đọc";
    };
    utterance.onerror = () => {
      if (btn) btn.innerHTML = "<span>🔊</span> Nghe Đọc";
    };

    window.speechSynthesis.speak(utterance);
  }

  /* ========================================================
     NAVIGATION & VIEW SWITCHING
     ======================================================== */
  switchView(viewName) {
    // Hide all view sections
    document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));
    
    // Update nav link active state
    document.querySelectorAll("#mainNav .nav-link").forEach(link => {
      if (link.dataset.view === viewName) {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });

    const target = document.getElementById(`view-${viewName}`);
    if (target) {
      target.classList.add("active");
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    // Lazy load view data
    if (viewName === "sets") {
      this.loadTestSets();
      this.loadStats();
    } else if (viewName === "mistakes") {
      this.loadMistakesView();
    } else if (viewName === "bookmarks") {
      this.loadBookmarksView();
    } else if (viewName === "stats") {
      this.loadStatsView();
    } else if (viewName === "custom") {
      this.loadCustomSetsDropdown();
    }
  }

  /* ========================================================
     DATA LOADING & API CALLS
     ======================================================== */
  async loadStats() {
    try {
      const res = await fetch("/api/stats");
      const data = await res.json();
      
      const setTxt = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
      };

      setTxt("dashTotalExams", data.total_exams);
      setTxt("dashAvgScore", `${data.avg_score}%`);
      setTxt("dashMistakes", data.active_mistakes);
      setTxt("dashTotalQuestions", data.total_questions);

      const mistakeBadge = document.getElementById("navMistakeBadge");
      if (mistakeBadge) {
        if (data.active_mistakes > 0) {
          mistakeBadge.textContent = data.active_mistakes;
          mistakeBadge.style.display = "inline-block";
        } else {
          mistakeBadge.style.display = "none";
        }
      }
    } catch (err) {
      console.error("Failed to load stats", err);
    }
  }

  async loadTestSets() {
    try {
      const res = await fetch("/api/sets");
      const data = await res.json();
      this.sets = data.sets || [];
      this.renderTestSets(this.sets);
    } catch (err) {
      console.error("Failed to load sets", err);
      const container = document.getElementById("testSetsContainer");
      if (container) container.innerHTML = `<div style="color:var(--danger); text-align:center; padding:2rem;">Không thể kết nối với server cục bộ. Vui lòng kiểm tra terminal backend!</div>`;
    }
  }

  renderTestSets(setsToRender) {
    const container = document.getElementById("testSetsContainer");
    if (!container) return;

    if (setsToRender.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding:3rem; color:var(--text-muted); grid-column:1/-1;">Không có bộ đề nào trong mục này.</div>`;
      return;
    }

    container.innerHTML = setsToRender.map(s => `
      <div class="set-card">
        <div>
          <div class="set-card-header">
            <span class="set-badge">${this.escapeHtml(s.badge || 'TOEIC')}</span>
            <span class="set-difficulty">${this.escapeHtml(s.difficulty || 'B1-B2')}</span>
          </div>
          <h4 class="set-title">${this.escapeHtml(s.title)}</h4>
          <p class="set-desc">${this.escapeHtml(s.description || 'Bộ đề kiểm tra chất lượng cao.')}</p>
        </div>

        <div>
          <div class="set-meta-info">
            <div class="meta-item"><span>📝</span> ${s.question_count || 0} câu hỏi</div>
            <div class="meta-item"><span>⏱️</span> ${s.time_limit || 15} phút</div>
            <div class="meta-item"><span>🏷️</span> ${this.escapeHtml(s.category)}</div>
          </div>
          <div class="set-actions">
            <button class="btn btn-secondary" onclick="app.startQuiz('${s.id}', 'practice')">
              <span>🎯</span> Luyện Tập
            </button>
            <button class="btn btn-primary" onclick="app.startQuiz('${s.id}', 'exam')">
              <span>⏱️</span> Thi Thử
            </button>
          </div>
        </div>
      </div>
    `).join("");
  }

  filterSets(category) {
    document.querySelectorAll("#categoryFilters .filter-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.filter === category);
    });

    if (category === "all") {
      this.renderTestSets(this.sets);
    } else {
      const filtered = this.sets.filter(s => s.category.toLowerCase().includes(category.toLowerCase()));
      this.renderTestSets(filtered);
    }
  }

  /* ========================================================
     QUIZ ENGINE: START, RENDER, QUESTIONS & ANSWERS
     ======================================================== */
  async startQuiz(setId, mode = "exam") {
    try {
      const res = await fetch(`/api/sets/${setId}`);
      if (!res.ok) throw new Error("Không thể tải bộ đề");
      const data = await res.json();

      this.activeSet = data;
      this.activeMode = mode;
      this.questions = data.questions || [];

      if (this.questions.length === 0) {
        this.showToast("Bộ đề này chưa có câu hỏi nào!");
        return;
      }

      // Reset test state
      this.currentIndex = 0;
      this.userAnswers = {};
      this.flaggedQuestions.clear();
      this.practiceRevealed = {};
      this.totalTimeSpent = 0;

      // Configure Header UI
      document.getElementById("quizTitle").textContent = data.title;
      const modeBadge = document.getElementById("quizModeBadge");
      modeBadge.textContent = mode === "exam" ? "Thi Thử (Bấm Giờ)" : "Luyện Tập (Xem Lời Giải)";
      modeBadge.className = `mode-pill ${mode}`;

      document.getElementById("quizSubMeta").textContent = `${this.questions.length} câu • ${data.time_limit} phút`;

      // Legend in practice mode
      document.getElementById("legendCorrectPractice").style.display = mode === "practice" ? "flex" : "none";
      document.getElementById("legendIncorrectPractice").style.display = mode === "practice" ? "flex" : "none";

      // Setup Timer
      const timerBox = document.getElementById("quizTimerBox");
      if (mode === "exam") {
        timerBox.style.display = "flex";
        this.timeRemaining = (data.time_limit || 15) * 60;
        this.startTimer();
      } else {
        timerBox.style.display = "none";
        this.stopTimer();
      }

      this.renderPalette();
      this.renderCurrentQuestion();
      this.switchView("quiz");

      this.showToast(`Bắt đầu: ${mode === 'exam' ? 'Chế độ Thi Thử' : 'Chế độ Luyện Tập'}`);
    } catch (err) {
      console.error(err);
      this.showToast("Lỗi khi mở bộ đề: " + err.message);
    }
  }

  startTimer() {
    this.stopTimer();
    this.updateTimerDisplay();

    this.timerInterval = setInterval(() => {
      this.timeRemaining--;
      this.totalTimeSpent++;
      this.updateTimerDisplay();

      if (this.timeRemaining <= 0) {
        this.stopTimer();
        this.showToast("Đã hết giờ làm bài! Tự động nộp bài thi.");
        this.finalizeExamSubmission();
      }
    }, 1000);
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  updateTimerDisplay() {
    const display = document.getElementById("timerDisplay");
    const box = document.getElementById("quizTimerBox");
    if (!display) return;

    const mins = Math.floor(Math.max(0, this.timeRemaining) / 60);
    const secs = Math.max(0, this.timeRemaining) % 60;
    display.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

    if (this.timeRemaining < 120 && this.timeRemaining > 0) {
      box.classList.add("timer-warning");
    } else {
      box.classList.remove("timer-warning");
    }
  }

  renderCurrentQuestion() {
    const q = this.questions[this.currentIndex];
    if (!q) return;

    // Badges & Audio
    document.getElementById("qCurrentNumberBadge").textContent = `Câu ${this.currentIndex + 1} / ${this.questions.length}`;
    document.getElementById("qCategoryBadge").textContent = q.category || 'General';

    // Bookmark icon state
    const starIcon = document.getElementById("bookmarkStarIcon");
    if (starIcon) {
      starIcon.textContent = q.is_bookmarked ? "★" : "☆";
      starIcon.style.color = q.is_bookmarked ? "var(--warning)" : "inherit";
    }

    // Bind Audio Play Button
    const btnAudio = document.getElementById("btnPlayAudio");
    btnAudio.onclick = () => this.speakText(q.question);

    // Sentence rendering: highlight ______
    const formattedSentence = this.escapeHtml(q.question).replace(/______/g, '<span class="blank">______</span>');
    document.getElementById("qSentenceText").innerHTML = formattedSentence;

    // Options rendering
    const container = document.getElementById("optionsContainer");
    const letters = ["A", "B", "C", "D"];
    const userSelected = this.userAnswers[q.id];
    const isPracticeRevealed = (this.activeMode === "practice" && userSelected !== undefined);

    container.innerHTML = q.options.map((opt, idx) => {
      let extraClass = "";
      if (this.activeMode === "exam") {
        if (userSelected === idx) extraClass = "selected";
      } else if (this.activeMode === "practice") {
        if (isPracticeRevealed) {
          if (idx === q.correct_answer) {
            extraClass = "correct disabled";
          } else if (userSelected === idx) {
            extraClass = "incorrect disabled";
          } else {
            extraClass = "disabled";
          }
        }
      }

      return `
        <div class="option-item ${extraClass}" onclick="app.selectOption(${idx})">
          <div class="option-letter">${letters[idx]}</div>
          <div class="option-text">${this.escapeHtml(opt)}</div>
        </div>
      `;
    }).join("");

    // Practice explanation card
    const expCard = document.getElementById("practiceExplanationCard");
    if (this.activeMode === "practice" && isPracticeRevealed) {
      expCard.style.display = "block";
      document.getElementById("expTranslationText").textContent = q.translation || "Chưa có dịch nghĩa";
      document.getElementById("expDetailText").textContent = q.explanation || "Chưa có giải thích";
      
      const vocabSec = document.getElementById("expVocabSection");
      const vocabList = document.getElementById("expVocabTags");
      if (q.vocab_notes) {
        vocabSec.style.display = "block";
        const notes = q.vocab_notes.split(";").map(n => n.trim()).filter(Boolean);
        vocabList.innerHTML = notes.map(n => `<span class="vocab-tag">${this.escapeHtml(n)}</span>`).join("");
      } else {
        vocabSec.style.display = "none";
      }
    } else {
      expCard.style.display = "none";
    }

    // Flag button text & state
    const flagBtn = document.getElementById("btnFlagQuestion");
    const isFlagged = this.flaggedQuestions.has(q.id);
    flagBtn.innerHTML = `<span>${isFlagged ? '🚩' : '🏳️'}</span> ${isFlagged ? 'Bỏ Đánh Dấu' : 'Đánh Dấu Xem Lại'}`;
    flagBtn.classList.toggle("btn-primary", isFlagged);
    flagBtn.classList.toggle("btn-outline", !isFlagged);

    // Prev / Next buttons
    document.getElementById("btnPrevQuestion").disabled = (this.currentIndex === 0);
    const nextBtn = document.getElementById("btnNextQuestion");
    if (this.currentIndex === this.questions.length - 1) {
      nextBtn.innerHTML = `<span>📝</span> Nộp Bài`;
    } else {
      nextBtn.innerHTML = `Câu Tiếp <span>▶</span>`;
    }

    // Update Progress Bar
    const pct = Math.round(((this.currentIndex + 1) / this.questions.length) * 100);
    document.getElementById("quizProgressBar").style.width = `${pct}%`;

    this.updatePaletteActiveItem();
  }

  selectOption(optIdx) {
    const q = this.questions[this.currentIndex];
    if (!q) return;

    if (this.activeMode === "practice" && this.userAnswers[q.id] !== undefined) {
      return; // Already answered this question in practice mode
    }

    this.userAnswers[q.id] = optIdx;

    if (this.activeMode === "practice") {
      const isCorrect = (optIdx === q.correct_answer);
      this.playSound(isCorrect ? "correct" : "wrong");
    } else {
      this.playSound("click");
    }

    this.renderCurrentQuestion();
    this.renderPalette();
  }

  prevQuestion() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.renderCurrentQuestion();
      this.playSound("click");
    }
  }

  nextQuestion() {
    if (this.currentIndex < this.questions.length - 1) {
      this.currentIndex++;
      this.renderCurrentQuestion();
      this.playSound("click");
    } else {
      this.openSubmitConfirmModal();
    }
  }

  goToQuestion(idx) {
    if (idx >= 0 && idx < this.questions.length) {
      this.currentIndex = idx;
      this.renderCurrentQuestion();
      this.playSound("click");
    }
  }

  toggleFlagCurrent() {
    const q = this.questions[this.currentIndex];
    if (!q) return;

    if (this.flaggedQuestions.has(q.id)) {
      this.flaggedQuestions.delete(q.id);
    } else {
      this.flaggedQuestions.add(q.id);
    }
    this.renderCurrentQuestion();
    this.renderPalette();
    this.playSound("click");
  }

  async toggleBookmarkCurrent() {
    const q = this.questions[this.currentIndex];
    if (!q) return;

    try {
      const res = await fetch(`/api/bookmark/${q.id}`, { method: "POST" });
      const data = await res.json();
      q.is_bookmarked = data.is_bookmarked;
      
      const starIcon = document.getElementById("bookmarkStarIcon");
      if (starIcon) {
        starIcon.textContent = q.is_bookmarked ? "★" : "☆";
        starIcon.style.color = q.is_bookmarked ? "var(--warning)" : "inherit";
      }

      this.showToast(q.is_bookmarked ? "Đã lưu vào câu hỏi quan tâm ⭐" : "Đã bỏ lưu câu hỏi");
      this.playSound("click");
    } catch (err) {
      console.error(err);
    }
  }

  /* ========================================================
     PALETTE & QUESTION STATUS NAVIGATION
     ======================================================== */
  renderPalette() {
    const grid = document.getElementById("paletteGrid");
    if (!grid) return;

    let answeredCount = 0;

    grid.innerHTML = this.questions.map((q, idx) => {
      const userChoice = this.userAnswers[q.id];
      const isAnswered = (userChoice !== undefined);
      const isFlagged = this.flaggedQuestions.has(q.id);
      const isCurrent = (this.currentIndex === idx);

      if (isAnswered) answeredCount++;

      let statusClass = "";
      if (this.activeMode === "practice" && isAnswered) {
        statusClass = (userChoice === q.correct_answer) ? "correct" : "incorrect";
      } else if (isAnswered) {
        statusClass = "answered";
      }

      if (isFlagged) statusClass += " flagged";
      if (isCurrent) statusClass += " active";

      return `
        <button class="palette-btn ${statusClass}" onclick="app.goToQuestion(${idx})">
          ${idx + 1}
        </button>
      `;
    }).join("");

    const countText = document.getElementById("paletteCountProgress");
    if (countText) {
      countText.textContent = `${answeredCount}/${this.questions.length} đã làm`;
    }
  }

  updatePaletteActiveItem() {
    const buttons = document.querySelectorAll("#paletteGrid .palette-btn");
    buttons.forEach((btn, idx) => {
      btn.classList.toggle("active", idx === this.currentIndex);
    });
  }

  /* ========================================================
     SUBMISSION & RESULTS
     ======================================================== */
  openSubmitConfirmModal() {
    const total = this.questions.length;
    let answered = 0;
    for (const q of this.questions) {
      if (this.userAnswers[q.id] !== undefined) answered++;
    }

    document.getElementById("modalAnsweredCount").textContent = `${answered}/${total}`;
    document.getElementById("modalUnansweredCount").textContent = `${total - answered}`;
    document.getElementById("modalFlaggedCount").textContent = `${this.flaggedQuestions.size}`;

    const modal = document.getElementById("submitModal");
    if (modal) modal.classList.add("active");
  }

  closeSubmitModal() {
    const modal = document.getElementById("submitModal");
    if (modal) modal.classList.remove("active");
  }

  confirmExitQuiz() {
    if (confirm("Bạn có chắc muốn thoát phòng thi? Tiến trình bài làm sẽ bị hủy.")) {
      this.stopTimer();
      this.switchView("sets");
    }
  }

  async finalizeExamSubmission() {
    this.closeSubmitModal();
    this.stopTimer();

    const timeSpent = this.activeMode === "exam" ? (this.totalTimeSpent || 1) : 30;

    try {
      const payload = {
        set_id: this.activeSet.id,
        set_title: this.activeSet.title,
        mode: this.activeMode,
        time_spent: timeSpent,
        answers: this.userAnswers
      };

      const res = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Gặp sự cố khi nộp bài");
      const result = await res.json();
      this.lastExamResult = result;

      this.renderResults(result);
      this.switchView("results");
      this.loadStats(); // refresh summary metrics

      if (result.percentage >= 80) {
        this.playSound("correct");
        this.showToast("Xuất sắc! Bạn đã đạt kết quả rất cao 🎉");
      } else {
        this.playSound("click");
      }
    } catch (err) {
      console.error(err);
      this.showToast("Lỗi khi nộp bài: " + err.message);
    }
  }

  renderResults(res) {
    // Score ring animation
    const circle = document.getElementById("scoreCircleFill");
    const circumference = 2 * Math.PI * 50; // r = 50 -> ~314.16
    const offset = circumference - (res.percentage / 100) * circumference;

    if (circle) {
      circle.style.strokeDashoffset = circumference;
      setTimeout(() => {
        circle.style.strokeDashoffset = offset;
      }, 100);
    }

    document.getElementById("resPercentScore").textContent = `${res.percentage}%`;
    document.getElementById("resFractionScore").textContent = `${res.score}/${res.total} Đúng`;

    // Headlines
    const headline = document.getElementById("resHeadline");
    const subline = document.getElementById("resSubline");

    if (res.percentage >= 90) {
      headline.textContent = "Xuất Sắc! Thành Tích Vượt Trội 🏆";
      subline.textContent = "Bạn đã nắm rất vững kiến thức phần này. Hãy giữ vững phong độ!";
    } else if (res.percentage >= 70) {
      headline.textContent = "Làm Tốt Lắm! Kết Quả Rất Đáng Khích Lệ 🌟";
      subline.textContent = "Bạn chỉ mắc một vài lỗi nhỏ, hãy xem kỹ phần giải thích chi tiết bên dưới nhé.";
    } else {
      headline.textContent = "Đừng Nản Lòng, Cố Gắng Lên Nào! 💪";
      subline.textContent = "Các câu làm sai đã được tự động lưu vào Sổ Tay Câu Sai để bạn ôn lại bất cứ lúc nào.";
    }

    // Numbers
    document.getElementById("resCorrectCount").textContent = res.score;
    document.getElementById("resWrongCount").textContent = (res.total - res.score);
    document.getElementById("resToeicScore").textContent = `~${res.toeic_scale}/495`;

    const mins = Math.floor(res.time_spent / 60);
    const secs = res.time_spent % 60;
    document.getElementById("resTimeSpent").textContent = `${mins}m ${secs}s`;

    // Button to redo only wrong
    const btnWrongOnly = document.getElementById("btnPracticeWrongOnly");
    if (res.score === res.total) {
      btnWrongOnly.style.display = "none";
    } else {
      btnWrongOnly.style.display = "inline-flex";
    }

    // Render detailed review list
    this.renderReviewList(res.detailed_results, "all");
  }

  renderReviewList(resultsList, filter = "all") {
    const container = document.getElementById("reviewListContainer");
    if (!container) return;

    let filtered = resultsList;
    if (filter === "wrong") {
      filtered = resultsList.filter(r => !r.is_correct);
    } else if (filter === "correct") {
      filtered = resultsList.filter(r => r.is_correct);
    }

    if (filtered.length === 0) {
      container.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Không có câu hỏi nào thỏa mãn bộ lọc.</div>`;
      return;
    }

    const letters = ["A", "B", "C", "D"];

    container.innerHTML = filtered.map((r, idx) => {
      const userLetter = r.user_choice >= 0 ? letters[r.user_choice] : "Chưa chọn";
      const correctLetter = letters[r.correct_choice];
      const isRight = r.is_correct;

      return `
        <div class="question-card" style="border-left: 4px solid ${isRight ? 'var(--success)' : 'var(--danger)'};">
          <div class="question-top-bar">
            <div style="display:flex; align-items:center; gap:0.5rem;">
              <span class="q-number-badge">Câu ${idx + 1}</span>
              <span class="q-category-tag">${this.escapeHtml(r.category || 'Grammar')}</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.75rem;">
              <button class="audio-tts-btn btn-sm" onclick="app.speakText('${this.escapeHtml(r.question)}')">
                <span>🔊</span> Nghe
              </button>
              <span style="font-weight:700; color:${isRight ? 'var(--success)' : 'var(--danger)'}">
                ${isRight ? '✅ Đúng (+1)' : '❌ Sai (0)'}
              </span>
            </div>
          </div>

          <div class="question-sentence" style="font-size: 1.15rem; margin-bottom: 1.25rem;">
            ${this.escapeHtml(r.question).replace(/______/g, '<span class="blank">______</span>')}
          </div>

          <div class="options-list" style="margin-bottom: 1.25rem;">
            ${r.options.map((opt, oIdx) => {
              let optClass = "disabled ";
              if (oIdx === r.correct_choice) optClass += "correct";
              else if (oIdx === r.user_choice && !isRight) optClass += "incorrect";

              return `
                <div class="option-item ${optClass}" style="padding: 0.75rem 1rem;">
                  <div class="option-letter">${letters[oIdx]}</div>
                  <div class="option-text">${this.escapeHtml(opt)}</div>
                  ${oIdx === r.correct_choice ? '<span style="color:var(--success); font-weight:700; margin-left:auto;">Đáp án chuẩn</span>' : ''}
                  ${oIdx === r.user_choice && !isRight ? '<span style="color:var(--danger); font-weight:700; margin-left:auto;">Lựa chọn của bạn</span>' : ''}
                </div>
              `;
            }).join("")}
          </div>

          <div class="explanation-card" style="display:block; margin-top:0;">
            <div class="explanation-header">
              <span>💡</span> Lời Giải & Dịch Nghĩa
            </div>
            <div class="explanation-section">
              <div class="explanation-label">📖 Dịch Nghĩa:</div>
              <div class="explanation-content">${this.escapeHtml(r.translation || 'Không có bản dịch')}</div>
            </div>
            <div class="explanation-section">
              <div class="explanation-label">🔍 Phân Tích:</div>
              <div class="explanation-content">${this.escapeHtml(r.explanation || 'Không có giải thích')}</div>
            </div>
          </div>
        </div>
      `;
    }).join("");
  }

  filterReview(filter) {
    document.querySelectorAll("#reviewFilters .filter-btn").forEach(btn => {
      btn.classList.toggle("active", btn.textContent.includes(filter === "wrong" ? "❌" : filter === "correct" ? "✅" : "Tất cả"));
    });
    if (this.lastExamResult) {
      this.renderReviewList(this.lastExamResult.detailed_results, filter);
    }
  }

  retakeCurrentSet() {
    if (this.activeSet) {
      this.startQuiz(this.activeSet.id, "exam");
    }
  }

  practiceWrongFromCurrentTest() {
    if (!this.lastExamResult) return;
    const wrongQuestionIds = new Set(
      this.lastExamResult.detailed_results
        .filter(r => !r.is_correct)
        .map(r => r.question_id)
    );

    const wrongQuestions = this.questions.filter(q => wrongQuestionIds.has(q.id));
    if (wrongQuestions.length === 0) {
      this.showToast("Không có câu hỏi sai nào!");
      return;
    }

    // Launch dedicated practice session for wrong questions
    this.questions = wrongQuestions;
    this.activeMode = "practice";
    this.currentIndex = 0;
    this.userAnswers = {};
    this.practiceRevealed = {};
    this.flaggedQuestions.clear();

    document.getElementById("quizTitle").textContent = `Ôn Tập Các Câu Sai (${this.activeSet.title})`;
    const modeBadge = document.getElementById("quizModeBadge");
    modeBadge.textContent = "Ôn Lại Câu Sai";
    modeBadge.className = "mode-pill practice";
    document.getElementById("quizTimerBox").style.display = "none";

    this.renderPalette();
    this.renderCurrentQuestion();
    this.switchView("quiz");
  }

  /* ========================================================
     MISTAKES & BOOKMARKS VIEWS
     ======================================================== */
  async loadMistakesView() {
    try {
      const res = await fetch("/api/mistakes");
      const data = await res.json();
      const mistakes = data.mistakes || [];
      const container = document.getElementById("mistakesListContainer");
      const btnPractice = document.getElementById("btnPracticeAllMistakes");

      if (mistakes.length === 0) {
        if (btnPractice) btnPractice.disabled = true;
        container.innerHTML = `
          <div class="question-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">🎉</div>
            <h3 style="margin-bottom:0.5rem;">Sổ Tay Câu Sai Đang Trống!</h3>
            <p style="color:var(--text-muted); max-width:500px; margin:0 auto;">
              Bạn chưa có câu nào bị sai hoặc bạn đã giải quyết thành thạo toàn bộ các câu trong sổ tay. Thật tuyệt vời!
            </p>
          </div>
        `;
        return;
      }

      if (btnPractice) btnPractice.disabled = false;

      container.innerHTML = mistakes.map(m => `
        <div class="mistake-item-card">
          <div class="question-top-bar">
            <div style="display:flex; align-items:center; gap:0.6rem;">
              <span class="mistake-badge-wrong">Sai ${m.wrong_count} lần</span>
              <span class="q-category-tag">${this.escapeHtml(m.set_title)} • ${this.escapeHtml(m.category || 'General')}</span>
            </div>
            <div style="display:flex; gap:0.5rem;">
              <button class="audio-tts-btn btn-sm" onclick="app.speakText('${this.escapeHtml(m.question)}')">
                <span>🔊</span> Nghe
              </button>
              <button class="btn btn-secondary btn-sm" onclick="app.resolveMistake(${m.question_id})">
                <span>✅</span> Đã Thành Thạo
              </button>
            </div>
          </div>

          <div style="font-size: 1.15rem; font-weight:600; margin-bottom:1rem;">
            ${this.escapeHtml(m.question).replace(/______/g, '<span class="blank">______</span>')}
          </div>

          <div style="background:var(--bg-surface-secondary); padding:1rem; border-radius:var(--radius-md); font-size:0.9rem;">
            <div style="margin-bottom:0.4rem;"><strong>Dịch nghĩa:</strong> ${this.escapeHtml(m.translation || '')}</div>
            <div style="color:var(--text-muted);"><strong>Giải thích:</strong> ${this.escapeHtml(m.explanation || '')}</div>
          </div>
        </div>
      `).join("");
    } catch (err) {
      console.error(err);
    }
  }

  async resolveMistake(qId) {
    try {
      await fetch(`/api/mistakes/${qId}/master`, { method: "POST" });
      this.showToast("Đã chuyển câu hỏi sang trạng thái Đã thành thạo! 🌟");
      this.playSound("correct");
      this.loadMistakesView();
      this.loadStats();
    } catch (err) {
      console.error(err);
    }
  }

  async startMistakesQuiz() {
    try {
      const res = await fetch("/api/mistakes");
      const data = await res.json();
      const mistakes = data.mistakes || [];
      if (mistakes.length === 0) return;

      this.activeSet = { id: "mistakes_custom", title: "Ôn Tập Sổ Tay Câu Sai", time_limit: 15 };
      this.questions = mistakes.map(m => ({
        id: m.question_id,
        question: m.question,
        options: m.options,
        correct_answer: m.correct_answer,
        translation: m.translation,
        explanation: m.explanation,
        category: m.category,
        difficulty: m.difficulty,
        vocab_notes: m.vocab_notes,
        is_bookmarked: false
      }));

      this.activeMode = "practice";
      this.currentIndex = 0;
      this.userAnswers = {};
      this.practiceRevealed = {};
      this.flaggedQuestions.clear();

      document.getElementById("quizTitle").textContent = "Ôn Tập Sổ Tay Câu Sai";
      const modeBadge = document.getElementById("quizModeBadge");
      modeBadge.textContent = "Chế Độ Sửa Lỗi";
      modeBadge.className = "mode-pill practice";
      document.getElementById("quizTimerBox").style.display = "none";

      this.renderPalette();
      this.renderCurrentQuestion();
      this.switchView("quiz");
    } catch (err) {
      console.error(err);
    }
  }

  async loadBookmarksView() {
    try {
      const res = await fetch("/api/bookmarks");
      const data = await res.json();
      const bookmarks = data.bookmarks || [];
      const container = document.getElementById("bookmarksListContainer");
      const btnPractice = document.getElementById("btnPracticeBookmarks");

      if (bookmarks.length === 0) {
        if (btnPractice) btnPractice.disabled = true;
        container.innerHTML = `
          <div class="question-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">⭐</div>
            <h3 style="margin-bottom:0.5rem;">Chưa Có Câu Hỏi Nào Được Đánh Dấu</h3>
            <p style="color:var(--text-muted); max-width:500px; margin:0 auto;">
              Trong lúc làm bài hoặc xem lời giải, bạn hãy bấm vào biểu tượng ngôi sao (☆) để lưu lại các câu hỏi tâm đắc nhé!
            </p>
          </div>
        `;
        return;
      }

      if (btnPractice) btnPractice.disabled = false;

      container.innerHTML = bookmarks.map(b => `
        <div class="mistake-item-card">
          <div class="question-top-bar">
            <div style="display:flex; align-items:center; gap:0.6rem;">
              <span class="set-badge">⭐ Đã lưu</span>
              <span class="q-category-tag">${this.escapeHtml(b.set_title)} • ${this.escapeHtml(b.category || 'General')}</span>
            </div>
            <div style="display:flex; gap:0.5rem;">
              <button class="audio-tts-btn btn-sm" onclick="app.speakText('${this.escapeHtml(b.question)}')">
                <span>🔊</span> Nghe
              </button>
              <button class="btn btn-outline btn-sm" onclick="app.removeBookmarkFromView(${b.question_id})">
                <span>✕</span> Bỏ Lưu
              </button>
            </div>
          </div>

          <div style="font-size: 1.15rem; font-weight:600; margin-bottom:1rem;">
            ${this.escapeHtml(b.question).replace(/______/g, '<span class="blank">______</span>')}
          </div>

          <div style="background:var(--bg-surface-secondary); padding:1rem; border-radius:var(--radius-md); font-size:0.9rem;">
            <div style="margin-bottom:0.4rem;"><strong>Dịch nghĩa:</strong> ${this.escapeHtml(b.translation || '')}</div>
            <div style="color:var(--text-muted);"><strong>Giải thích:</strong> ${this.escapeHtml(b.explanation || '')}</div>
          </div>
        </div>
      `).join("");
    } catch (err) {
      console.error(err);
    }
  }

  async removeBookmarkFromView(qId) {
    await fetch(`/api/bookmark/${qId}`, { method: "POST" });
    this.showToast("Đã bỏ lưu câu hỏi");
    this.loadBookmarksView();
    this.loadStats();
  }

  async startBookmarksQuiz() {
    try {
      const res = await fetch("/api/bookmarks");
      const data = await res.json();
      const bookmarks = data.bookmarks || [];
      if (bookmarks.length === 0) return;

      this.activeSet = { id: "bookmarks_custom", title: "Luyện Tập Câu Hỏi Đã Lưu", time_limit: 15 };
      this.questions = bookmarks.map(b => ({
        id: b.question_id,
        question: b.question,
        options: b.options,
        correct_answer: b.correct_answer,
        translation: b.translation,
        explanation: b.explanation,
        category: b.category,
        difficulty: b.difficulty,
        vocab_notes: b.vocab_notes,
        is_bookmarked: true
      }));

      this.activeMode = "practice";
      this.currentIndex = 0;
      this.userAnswers = {};
      this.practiceRevealed = {};
      this.flaggedQuestions.clear();

      document.getElementById("quizTitle").textContent = "Luyện Tập Câu Đã Lưu ⭐";
      const modeBadge = document.getElementById("quizModeBadge");
      modeBadge.textContent = "Chế Độ Đã Lưu";
      modeBadge.className = "mode-pill practice";
      document.getElementById("quizTimerBox").style.display = "none";

      this.renderPalette();
      this.renderCurrentQuestion();
      this.switchView("quiz");
    } catch (err) {
      console.error(err);
    }
  }

  /* ========================================================
     STATS & HISTORY TABLE VIEW
     ======================================================== */
  async loadStatsView() {
    try {
      const res = await fetch("/api/stats");
      const data = await res.json();

      document.getElementById("statsTotalExams").textContent = data.total_exams;
      document.getElementById("statsAvgScore").textContent = `${data.avg_score}%`;
      document.getElementById("statsTotalTime").textContent = `${data.total_time_minutes} phút`;
      document.getElementById("statsActiveMistakes").textContent = data.active_mistakes;

      const tbody = document.getElementById("historyTableBody");
      const history = data.recent_history || [];

      if (history.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding:2rem;">Chưa có lịch sử làm bài nào. Hãy thử làm một đề thi nhé!</td></tr>`;
        return;
      }

      tbody.innerHTML = history.map(h => {
        const mins = Math.floor(h.time_spent / 60);
        const secs = h.time_spent % 60;
        return `
          <tr>
            <td>${this.escapeHtml(h.date_completed || '')}</td>
            <td><strong>${this.escapeHtml(h.set_title || 'Đề thi')}</strong></td>
            <td><span class="mode-pill ${h.mode === 'exam' ? 'exam' : 'practice'}" style="font-size:0.75rem;">${h.mode === 'exam' ? 'Thi thử' : 'Luyện tập'}</span></td>
            <td><strong style="color:var(--primary);">${h.score} / ${h.total_questions}</strong></td>
            <td><strong>${h.percentage}%</strong></td>
            <td>${mins}m ${secs}s</td>
            <td>
              <button class="btn btn-outline btn-sm" onclick="app.viewPastExam(${h.id})">
                <span>🔍</span> Xem lại
              </button>
            </td>
          </tr>
        `;
      }).join("");
    } catch (err) {
      console.error(err);
    }
  }

  async viewPastExam(historyId) {
    try {
      const res = await fetch(`/api/history/${historyId}`);
      if (!res.ok) throw new Error("Không thể tải lịch sử");
      const data = await res.json();

      this.lastExamResult = {
        score: data.score,
        total: data.total_questions,
        percentage: data.percentage,
        toeic_scale: Math.round((data.score / data.total_questions) * 495),
        time_spent: data.time_spent,
        detailed_results: data.review_list
      };

      this.renderResults(this.lastExamResult);
      this.switchView("results");
    } catch (err) {
      console.error(err);
      this.showToast("Không thể tải chi tiết bài thi");
    }
  }

  /* ========================================================
     CUSTOM QUESTION & JSON IMPORT
     ======================================================== */
  async loadCustomSetsDropdown() {
    const sel = document.getElementById("customSetSelect");
    if (!sel) return;

    if (this.sets.length === 0) {
      await this.loadTestSets();
    }

    sel.innerHTML = this.sets.map(s => `
      <option value="${s.id}">${this.escapeHtml(s.title)} (${s.question_count || 0} câu)</option>
    `).join("");
  }

  async handleCreateQuestion(e) {
    e.preventDefault();

    const payload = {
      set_id: document.getElementById("customSetSelect").value,
      question: document.getElementById("cqText").value.trim(),
      options: [
        document.getElementById("cqOptA").value.trim(),
        document.getElementById("cqOptB").value.trim(),
        document.getElementById("cqOptC").value.trim(),
        document.getElementById("cqOptD").value.trim(),
      ],
      correct_answer: parseInt(document.getElementById("cqCorrect").value),
      category: document.getElementById("cqCategory").value.trim() || "Chung",
      translation: document.getElementById("cqTranslation").value.trim(),
      explanation: document.getElementById("cqExplanation").value.trim(),
      vocab_notes: document.getElementById("cqVocab").value.trim(),
      difficulty: "B1"
    };

    try {
      const res = await fetch("/api/questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Không thể lưu câu hỏi");

      this.showToast("Đã thêm câu hỏi thành công vào database! 🎉");
      this.playSound("correct");
      document.getElementById("formAddQuestion").reset();
      this.loadTestSets();
      this.loadStats();
    } catch (err) {
      this.showToast("Lỗi: " + err.message);
    }
  }

  fillSampleJson() {
    const sample = {
      set: {
        id: "custom_unit_01",
        title: "Đề Tự Tạo: 10 Câu Bẫy Giới Từ & Cụm Động Từ",
        description: "Bộ câu hỏi tự biên soạn về các cặp giới từ và phrasal verbs phổ biến.",
        category: "Tự Tạo",
        difficulty: "B1-B2",
        time_limit: 10,
        badge: "Custom"
      },
      questions: [
        {
          question: "The project manager is responsible ______ delivering the project milestones on schedule.",
          options: ["for", "with", "about", "to"],
          correct_answer: 0,
          translation: "Người quản lý dự án chịu trách nhiệm bàn giao các cột mốc dự án đúng tiến độ.",
          explanation: "Cấu trúc cố định: 'responsible for + V-ing/Noun' (chịu trách nhiệm về cái gì).",
          category: "Prepositions",
          vocab_notes: "responsible for: chịu trách nhiệm; milestone: cột mốc tiến độ."
        },
        {
          question: "Due to unforeseen weather conditions, the outdoor charity event had to be ______ until next month.",
          options: ["called off", "put off", "taken over", "run out"],
          correct_answer: 1,
          translation: "Do điều kiện thời tiết bất khả kháng, sự kiện từ thiện ngoài trời đã phải dời lại tới tháng sau.",
          explanation: "'Put off' = postpone (dời lại lịch). 'Called off' = cancel (hủy bỏ hoàn toàn).",
          category: "Phrasal Verbs",
          vocab_notes: "unforeseen (adj): bất ngờ, không lường trước; put off: hoãn lại."
        }
      ]
    };

    const area = document.getElementById("jsonInputArea");
    if (area) {
      area.value = JSON.stringify(sample, null, 2);
      document.getElementById("detectedFormatBadge").textContent = "Đang ở định dạng JSON";
    }
  }

  fillSampleTxt() {
    const sampleText = `Câu 1: All employees are required to wear their ID badges ______ inside the corporate headquarters.
A. while
B. during
C. because
D. despite
Đáp án: A
Giải thích: "While inside" là dạng rút gọn của mệnh đề trạng ngữ "while they are inside".
Dịch: Tất cả nhân viên đều được yêu cầu đeo thẻ tên khi ở bên trong trụ sở công ty.
Từ vựng: corporate headquarters: trụ sở chính tập đoàn; ID badge: thẻ nhân viên.

Câu 2: Ms. Clara is by far the most ______ candidate interviewed for the senior marketing specialist role.
A. qualification
B. qualify
C. qualified
D. qualifying
Đáp án: C
Giải thích: Sau "the most" cần tính từ chỉ phẩm chất "qualified" (có năng lực, đủ tiêu chuẩn).
Dịch: Cô Clara là ứng viên có năng lực tốt nhất trong số những người được phỏng vấn.
Từ vựng: qualified (adj): có trình độ/năng lực; candidate: ứng viên.`;

    const area = document.getElementById("jsonInputArea");
    if (area) {
      area.value = sampleText;
      document.getElementById("detectedFormatBadge").textContent = "Đang ở định dạng Văn bản Text/Word";
    }
  }

  handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const label = document.getElementById("uploadedFileName");
    if (label) label.textContent = `Đã chọn: ${file.name} (${Math.round(file.size / 1024)} KB)`;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target.result;
      const area = document.getElementById("jsonInputArea");
      if (area) {
        area.value = content;
        const isJson = content.trim().startsWith("{") || content.trim().startsWith("[");
        document.getElementById("detectedFormatBadge").textContent = isJson ? "File JSON nhận diện thành công" : "File Text/Word nhận diện thành công";
        this.showToast(`Đã đọc nội dung từ file ${file.name}!`);
      }
    };
    reader.onerror = () => {
      this.showToast("Lỗi khi đọc file trên máy tính");
    };
    reader.readAsText(file, "UTF-8");
  }

  parsePlainTextInput(text) {
    const lines = text.split("\n");
    const questions = [];
    let currentQ = null;
    let options = {};
    let correct = 0;
    let explanation = "";
    let translation = "";
    let vocab = "";

    const saveCurrent = () => {
      if (currentQ && Object.keys(options).length >= 2) {
        const optsList = [
          options["A"] || "",
          options["B"] || "",
          options["C"] || "",
          options["D"] || ""
        ];
        questions.push({
          question: currentQ.trim(),
          options: optsList,
          correct_answer: correct,
          explanation: explanation.trim(),
          translation: translation.trim(),
          vocab_notes: vocab.trim(),
          category: "Tự nạp Text",
          difficulty: "B1"
        });
      }
      currentQ = null;
      options = {};
      correct = 0;
      explanation = "";
      translation = "";
      vocab = "";
    };

    for (let raw of lines) {
      const line = raw.trim();
      if (!line) continue;

      // Match question start
      const qMatch = line.match(/^(?:Câu\s*\d+[\.:]?|Question\s*\d+[\.:]?|\d+[\.:])\s*(.*)/i);
      if (qMatch) {
        saveCurrent();
        currentQ = qMatch[1].trim();
        continue;
      }

      // Match options A., B., C., D.
      const optMatch = line.match(/^([A-D])[\.:\)]\s*(.*)/i);
      if (optMatch && currentQ) {
        const letter = optMatch[1].toUpperCase();
        options[letter] = optMatch[2].trim();
        continue;
      }

      // Match Answer
      const ansMatch = line.match(/^(?:Đáp án|Answer|Key|Đ\/A)[\s:]*([A-D])/i);
      if (ansMatch) {
        const letter = ansMatch[1].toUpperCase();
        correct = { "A": 0, "B": 1, "C": 2, "D": 3 }[letter] ?? 0;
        continue;
      }

      // Match Explanation
      const expMatch = line.match(/^(?:Giải thích|Explanation|Chi tiết)[\s:]*(.*)/i);
      if (expMatch) {
        explanation = expMatch[1].trim();
        continue;
      }

      // Match Translation
      const transMatch = line.match(/^(?:Dịch nghĩa|Dịch|Translation)[\s:]*(.*)/i);
      if (transMatch) {
        translation = transMatch[1].trim();
        continue;
      }

      // Match Vocab
      const vocabMatch = line.match(/^(?:Từ vựng|Vocab)[\s:]*(.*)/i);
      if (vocabMatch) {
        vocab = vocabMatch[1].trim();
        continue;
      }

      // Append multi-line question text if before options
      if (currentQ && Object.keys(options).length === 0) {
        currentQ += " " + line;
      }
    }

    saveCurrent();

    const timestamp = Date.now().toString().slice(-4);
    return {
      set: {
        id: `custom_set_${timestamp}`,
        title: `Bộ Đề Nạp Tự Do #${timestamp}`,
        description: `Bộ đề tự nạp gồm ${questions.length} câu trắc nghiệm.`,
        category: "Tự Nạp",
        difficulty: "B1 - B2",
        time_limit: Math.max(5, Math.round(questions.length * 0.75)),
        badge: "Imported"
      },
      questions: questions
    };
  }

  async handleImportBulk(e) {
    e.preventDefault();
    const area = document.getElementById("jsonInputArea");
    if (!area || !area.value.trim()) {
      this.showToast("Vui lòng nhập hoặc dán nội dung đề thi!");
      return;
    }

    const content = area.value.trim();
    let payload = null;

    if (content.startsWith("{")) {
      try {
        payload = JSON.parse(content);
      } catch (err) {
        this.showToast("Lỗi cú pháp JSON: " + err.message);
        return;
      }
    } else {
      // Parse plain text
      payload = this.parsePlainTextInput(content);
      if (!payload.questions || payload.questions.length === 0) {
        this.showToast("Không tìm thấy câu hỏi hợp lệ trong văn bản! Vui lòng xem Mẫu Text/Word.");
        return;
      }
    }

    try {
      const res = await fetch("/api/import-json", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Lỗi khi nhập dữ liệu");
      }

      const result = await res.json();
      this.showToast(result.message || "Đã nạp thành công bộ đề!");
      this.playSound("correct");
      this.loadTestSets();
      this.loadStats();
      this.switchView("sets");
    } catch (err) {
      this.showToast("Lỗi khi nạp đề: " + err.message);
    }
  }

  /* ========================================================
     KEYBOARD SHORTCUTS
     ======================================================== */
  setupKeyboardShortcuts() {
    window.addEventListener("keydown", (e) => {
      // Ignore if typing inside form inputs
      if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
        return;
      }

      const quizView = document.getElementById("view-quiz");
      if (!quizView || !quizView.classList.contains("active")) return;

      const key = e.key.toUpperCase();
      if (key === "A" || key === "1") this.selectOption(0);
      else if (key === "B" || key === "2") this.selectOption(1);
      else if (key === "C" || key === "3") this.selectOption(2);
      else if (key === "D" || key === "4") this.selectOption(3);
      else if (e.key === "ArrowLeft") this.prevQuestion();
      else if (e.key === "ArrowRight") this.nextQuestion();
      else if (key === "F") this.toggleFlagCurrent();
    });
  }

  /* ========================================================
     TOAST NOTIFICATIONS & UTILS
     ======================================================== */
  showToast(message) {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `<span>⚡</span> <span>${this.escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }

  escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

// Global App Instance
const app = new QuizApp();
window.app = app;
