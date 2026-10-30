import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.database import (
    get_connection,
    record_exam_history,
    toggle_bookmark,
    get_stats_summary
)

router = APIRouter(prefix="/api")

class SubmitRequest(BaseModel):
    set_id: str
    set_title: str
    mode: str = "exam" # 'exam' or 'practice'
    time_spent: int # seconds
    answers: Dict[str, int] # { "question_id": selected_option_index }

class QuestionCreate(BaseModel):
    set_id: str
    question: str
    options: List[str]
    correct_answer: int
    translation: Optional[str] = ""
    explanation: Optional[str] = ""
    category: Optional[str] = "Chung"
    difficulty: Optional[str] = "B1"
    vocab_notes: Optional[str] = ""

class SetCreate(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    category: str = "Tự tạo"
    difficulty: str = "B1"
    time_limit: int = 15
    badge: str = "Custom"

@router.get("/sets")
def get_test_sets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.id, s.title, s.description, s.category, s.difficulty, s.time_limit, s.badge, s.created_at,
           COUNT(q.id) as question_count
    FROM test_sets s
    LEFT JOIN questions q ON s.id = q.set_id
    GROUP BY s.id
    ORDER BY s.rowid ASC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"sets": rows}

@router.get("/sets/{set_id}")
def get_set_details(set_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_sets WHERE id = ?", (set_id,))
    set_row = cursor.fetchone()
    if not set_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy bộ đề")

    cursor.execute("""
    SELECT q.id, q.set_id, q.question, q.options, q.correct_answer, q.translation,
           q.explanation, q.category, q.difficulty, q.vocab_notes,
           (SELECT COUNT(*) FROM bookmarks b WHERE b.question_id = q.id) as is_bookmarked
    FROM questions q
    WHERE q.set_id = ?
    ORDER BY q.id ASC
    """, (set_id,))
    q_rows = cursor.fetchall()
    conn.close()

    questions = []
    for r in q_rows:
        item = dict(r)
        item["options"] = json.loads(item["options"]) if isinstance(item["options"], str) else item["options"]
        item["is_bookmarked"] = bool(item["is_bookmarked"])
        questions.append(item)

    result = dict(set_row)
    result["questions"] = questions
    return result

@router.post("/submit")
def submit_exam(payload: SubmitRequest):
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch all questions for this set to verify answers
    cursor.execute("SELECT id, question, options, correct_answer, translation, explanation, category FROM questions WHERE set_id = ?", (payload.set_id,))
    db_questions = cursor.fetchall()
    conn.close()

    total = len(db_questions)
    if total == 0:
        raise HTTPException(status_code=400, detail="Bộ đề không có câu hỏi nào")

    score = 0
    detailed_results = []

    for q in db_questions:
        q_id = q["id"]
        q_id_str = str(q_id)
        user_choice = payload.answers.get(q_id_str, -1)
        correct_choice = q["correct_answer"]
        is_correct = (user_choice == correct_choice)

        if is_correct:
            score += 1

        opts = json.loads(q["options"]) if isinstance(q["options"], str) else q["options"]
        detailed_results.append({
            "question_id": q_id,
            "question": q["question"],
            "options": opts,
            "user_choice": user_choice,
            "correct_choice": correct_choice,
            "is_correct": is_correct,
            "translation": q["translation"],
            "explanation": q["explanation"],
            "category": q["category"]
        })

    # Save to history & mistakes tracking
    record_exam_history(
        set_id=payload.set_id,
        set_title=payload.set_title,
        mode=payload.mode,
        score=score,
        total=total,
        time_spent=payload.time_spent,
        answers=payload.answers
    )

    percentage = round((score / total) * 100, 1)

    # TOEIC estimated scaled score (for 20 questions scaled to ~495 Reading equivalent)
    toeic_scale = round((score / total) * 495)

    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "toeic_scale": toeic_scale,
        "time_spent": payload.time_spent,
        "detailed_results": detailed_results
    }

@router.get("/history")
def get_history(limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, set_id, set_title, mode, score, total_questions, percentage, time_spent, date_completed
    FROM exam_history
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"history": rows}

@router.get("/history/{history_id}")
def get_history_detail(history_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exam_history WHERE id = ?", (history_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch sử bài thi")

    history_item = dict(row)
    answers = json.loads(history_item.get("answers_json") or "{}")

    # Get the questions
    cursor.execute("SELECT id, question, options, correct_answer, translation, explanation, category FROM questions WHERE set_id = ?", (history_item["set_id"],))
    q_rows = cursor.fetchall()
    conn.close()

    review_list = []
    for q in q_rows:
        qid_str = str(q["id"])
        user_choice = answers.get(qid_str, -1)
        opts = json.loads(q["options"]) if isinstance(q["options"], str) else q["options"]
        review_list.append({
            "question_id": q["id"],
            "question": q["question"],
            "options": opts,
            "user_choice": user_choice,
            "correct_choice": q["correct_answer"],
            "is_correct": user_choice == q["correct_answer"],
            "translation": q["translation"],
            "explanation": q["explanation"],
            "category": q["category"]
        })

    history_item["review_list"] = review_list
    return history_item

@router.get("/mistakes")
def get_mistakes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT m.id as mistake_id, m.wrong_count, m.last_attempt_date, m.mastered,
           q.id as question_id, q.set_id, q.question, q.options, q.correct_answer,
           q.translation, q.explanation, q.category, q.difficulty, q.vocab_notes,
           s.title as set_title
    FROM mistakes m
    JOIN questions q ON m.question_id = q.id
    JOIN test_sets s ON q.set_id = s.id
    WHERE m.mastered = 0
    ORDER BY m.wrong_count DESC, m.last_attempt_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    items = []
    for r in rows:
        item = dict(r)
        item["options"] = json.loads(item["options"]) if isinstance(item["options"], str) else item["options"]
        items.append(item)
    return {"mistakes": items}

@router.post("/mistakes/{question_id}/master")
def mark_mistake_mastered(question_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE mistakes SET mastered = 1 WHERE question_id = ?", (question_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Đã đánh dấu đã thành thạo!"}

@router.post("/mistakes/{question_id}/reset")
def reset_mistake(question_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mistakes WHERE question_id = ?", (question_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Đã xóa khỏi sổ tay câu sai"}

@router.post("/bookmark/{question_id}")
def api_toggle_bookmark(question_id: int):
    is_bookmarked = toggle_bookmark(question_id)
    return {"is_bookmarked": is_bookmarked}

@router.get("/bookmarks")
def get_all_bookmarks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT b.id as bookmark_id, b.created_at as bookmarked_at,
           q.id as question_id, q.set_id, q.question, q.options, q.correct_answer,
           q.translation, q.explanation, q.category, q.difficulty, q.vocab_notes,
           s.title as set_title
    FROM bookmarks b
    JOIN questions q ON b.question_id = q.id
    JOIN test_sets s ON q.set_id = s.id
    ORDER BY b.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    items = []
    for r in rows:
        item = dict(r)
        item["options"] = json.loads(item["options"]) if isinstance(item["options"], str) else item["options"]
        items.append(item)
    return {"bookmarks": items}

@router.get("/stats")
def get_stats():
    return get_stats_summary()

@router.post("/sets")
def create_set(item: SetCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM test_sets WHERE id = ?", (item.id,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Mã bộ đề đã tồn tại")

    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO test_sets (id, title, description, category, difficulty, time_limit, badge, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (item.id, item.title, item.description, item.category, item.difficulty, item.time_limit, item.badge, now))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Đã tạo bộ đề thành công", "id": item.id}

@router.post("/questions")
def create_question(item: QuestionCreate):
    conn = get_connection()
    cursor = conn.cursor()
    # Check if set exists
    cursor.execute("SELECT id FROM test_sets WHERE id = ?", (item.set_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy bộ đề tương ứng")

    cursor.execute("""
    INSERT INTO questions (set_id, question, options, correct_answer, translation, explanation, category, difficulty, vocab_notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item.set_id,
        item.question,
        json.dumps(item.options, ensure_ascii=False),
        item.correct_answer,
        item.translation,
        item.explanation,
        item.category,
        item.difficulty,
        item.vocab_notes
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"success": True, "message": "Đã thêm câu hỏi thành công", "id": new_id}

@router.post("/import-json")
def import_from_json(payload: Dict[str, Any]):
    """Bulk import sets and questions from a JSON payload"""
    conn = get_connection()
    cursor = conn.cursor()

    set_info = payload.get("set")
    questions = payload.get("questions", [])

    if not set_info or not questions:
        conn.close()
        raise HTTPException(status_code=400, detail="Payload phải chứa 'set' và danh sách 'questions'")

    set_id = set_info.get("id")
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT OR REPLACE INTO test_sets (id, title, description, category, difficulty, time_limit, badge, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        set_id,
        set_info.get("title", "Đề mới nhập"),
        set_info.get("description", ""),
        set_info.get("category", "Tự nhập"),
        set_info.get("difficulty", "B1"),
        set_info.get("time_limit", 15),
        set_info.get("badge", "Imported"),
        now
    ))

    added_count = 0
    for q in questions:
        cursor.execute("""
        INSERT INTO questions (set_id, question, options, correct_answer, translation, explanation, category, difficulty, vocab_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            set_id,
            q["question"],
            json.dumps(q["options"], ensure_ascii=False),
            q.get("correct_answer", 0),
            q.get("translation", ""),
            q.get("explanation", ""),
            q.get("category", "General"),
            q.get("difficulty", "B1"),
            q.get("vocab_notes", "")
        ))
        added_count += 1

    conn.commit()
    conn.close()
    return {"success": True, "message": f"Đã nhập thành công bộ đề '{set_info.get('title')}' với {added_count} câu hỏi."}
