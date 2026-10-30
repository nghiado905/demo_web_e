import sqlite3
import json
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "quiz_data.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Table for Test Sets / Question Sets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_sets (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Trung bình',
        time_limit INTEGER DEFAULT 20,
        badge TEXT DEFAULT 'TOEIC',
        created_at TEXT
    )
    """)

    # Table for Questions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        set_id TEXT NOT NULL,
        question TEXT NOT NULL,
        options TEXT NOT NULL,
        correct_answer INTEGER NOT NULL,
        translation TEXT,
        explanation TEXT,
        category TEXT,
        difficulty TEXT DEFAULT 'B1',
        vocab_notes TEXT,
        FOREIGN KEY (set_id) REFERENCES test_sets(id) ON DELETE CASCADE
    )
    """)

    # Table for Exam / Practice History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exam_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        set_id TEXT,
        set_title TEXT,
        mode TEXT DEFAULT 'exam',
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        percentage REAL NOT NULL,
        time_spent INTEGER NOT NULL,
        date_completed TEXT,
        answers_json TEXT
    )
    """)

    # Table for Mistakes (Sổ tay câu hỏi sai)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mistakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER UNIQUE,
        wrong_count INTEGER DEFAULT 1,
        last_attempt_date TEXT,
        mastered INTEGER DEFAULT 0,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
    )
    """)

    # Table for Bookmarked questions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER UNIQUE,
        created_at TEXT,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

def record_exam_history(set_id: str, set_title: str, mode: str, score: int, total: int, time_spent: int, answers: dict):
    conn = get_connection()
    cursor = conn.cursor()
    pct = round((score / total) * 100, 1) if total > 0 else 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO exam_history (set_id, set_title, mode, score, total_questions, percentage, time_spent, date_completed, answers_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (set_id, set_title, mode, score, total, pct, time_spent, now, json.dumps(answers, ensure_ascii=False)))

    # Process mistakes if any question was answered incorrectly
    for q_id_str, user_ans in answers.items():
        try:
            q_id = int(q_id_str)
            # Find correct answer
            cursor.execute("SELECT correct_answer FROM questions WHERE id = ?", (q_id,))
            row = cursor.fetchone()
            if row:
                correct = row["correct_answer"]
                if user_ans != correct:
                    # Record or increment mistake
                    cursor.execute("""
                    INSERT INTO mistakes (question_id, wrong_count, last_attempt_date, mastered)
                    VALUES (?, 1, ?, 0)
                    ON CONFLICT(question_id) DO UPDATE SET
                        wrong_count = wrong_count + 1,
                        last_attempt_date = excluded.last_attempt_date,
                        mastered = 0
                    """, (q_id, now))
                elif user_ans == correct:
                    # If previously in mistakes, mark as mastered if answered correctly twice or just keep track
                    cursor.execute("""
                    UPDATE mistakes SET mastered = 1 WHERE question_id = ?
                    """, (q_id,))
        except Exception:
            continue

    conn.commit()
    conn.close()

def toggle_bookmark(question_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM bookmarks WHERE question_id = ?", (question_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM bookmarks WHERE question_id = ?", (question_id,))
        is_bookmarked = False
    else:
        cursor.execute("INSERT INTO bookmarks (question_id, created_at) VALUES (?, ?)",
                       (question_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        is_bookmarked = True
    conn.commit()
    conn.close()
    return is_bookmarked

def get_stats_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total_exams, AVG(percentage) as avg_score, SUM(time_spent) as total_time FROM exam_history")
    summary = dict(cursor.fetchone() or {})

    cursor.execute("SELECT COUNT(*) as total_questions FROM questions")
    q_count = cursor.fetchone()["total_questions"]

    cursor.execute("SELECT COUNT(*) as total_mistakes FROM mistakes WHERE mastered = 0")
    m_count = cursor.fetchone()["total_mistakes"]

    cursor.execute("SELECT COUNT(*) as total_bookmarks FROM bookmarks")
    b_count = cursor.fetchone()["total_bookmarks"]

    cursor.execute("""
    SELECT id, set_title, mode, score, total_questions, percentage, time_spent, date_completed
    FROM exam_history ORDER BY id DESC LIMIT 10
    """)
    recent_history = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "total_exams": summary.get("total_exams") or 0,
        "avg_score": round(summary.get("avg_score") or 0, 1),
        "total_time_minutes": round((summary.get("total_time") or 0) / 60, 1),
        "total_questions": q_count,
        "active_mistakes": m_count,
        "total_bookmarks": b_count,
        "recent_history": recent_history
    }
