import json
import sys
import os
import re

# Ensure Windows terminal doesn't crash on UTF-8 characters
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.database import get_connection, init_db

def parse_txt_exam(content, default_set_id="custom_txt_set", default_title="Bộ Đề Từ File Text"):
    """
    Parses plain text exam format:
    Câu 1: Question text...
    A. option 1
    B. option 2
    C. option 3
    D. option 4
    Đáp án: A (or Key: A / Answer: A)
    Giải thích: ...
    Dịch: ...
    """
    lines = content.splitlines()
    questions = []
    
    current_q = None
    options = {}
    correct = 0
    explanation = ""
    translation = ""
    vocab = ""
    
    def save_current():
        nonlocal current_q, options, correct, explanation, translation, vocab
        if current_q and len(options) >= 2:
            opts_list = [
                options.get("A", ""),
                options.get("B", ""),
                options.get("C", ""),
                options.get("D", "")
            ]
            questions.append({
                "question": current_q.strip(),
                "options": opts_list,
                "correct_answer": correct,
                "explanation": explanation.strip(),
                "translation": translation.strip(),
                "vocab_notes": vocab.strip(),
                "category": "Tổng hợp",
                "difficulty": "B1"
            })
        current_q = None
        options = {}
        correct = 0
        explanation = ""
        translation = ""
        vocab = ""

    for line in lines:
        raw = line.strip()
        if not raw:
            continue

        # Check question start (e.g., "1.", "Câu 1:", "Question 1:")
        q_match = re.match(r"^(?:Câu\s*\d+[\.:]?|Question\s*\d+[\.:]?|\d+[\.:])\s*(.*)", raw, re.IGNORECASE)
        if q_match:
            save_current()
            current_q = q_match.group(1).strip()
            continue

        # Check options A., B., C., D.
        opt_match = re.match(r"^([A-D])[\.:\)]\s*(.*)", raw, re.IGNORECASE)
        if opt_match and current_q:
            letter = opt_match.group(1).upper()
            options[letter] = opt_match.group(2).strip()
            continue

        # Check Answer: "Đáp án: A", "Answer: B", "Key: C"
        ans_match = re.match(r"^(?:Đáp án|Answer|Key|Đ/A)[\s:]*([A-D])", raw, re.IGNORECASE)
        if ans_match:
            letter = ans_match.group(1).upper()
            correct = {"A": 0, "B": 1, "C": 2, "D": 3}.get(letter, 0)
            continue

        # Check Explanation
        exp_match = re.match(r"^(?:Giải thích|Explanation|Chi tiết)[\s:]*(.*)", raw, re.IGNORECASE)
        if exp_match:
            explanation = exp_match.group(1).strip()
            continue

        # Check Translation
        trans_match = re.match(r"^(?:Dịch nghĩa|Dịch|Translation)[\s:]*(.*)", raw, re.IGNORECASE)
        if trans_match:
            translation = trans_match.group(1).strip()
            continue

        # Check Vocab
        vocab_match = re.match(r"^(?:Từ vựng|Vocab)[\s:]*(.*)", raw, re.IGNORECASE)
        if vocab_match:
            vocab = vocab_match.group(1).strip()
            continue

        # If current question is being accumulated
        if current_q and len(options) == 0:
            current_q += " " + raw

    save_current()

    return {
        "set": {
            "id": default_set_id,
            "title": default_title,
            "description": f"Đề thi tự nạp gồm {len(questions)} câu hỏi.",
            "category": "Tự Nạp",
            "difficulty": "B1 - B2",
            "time_limit": max(5, round(len(questions) * 0.75)),
            "badge": "Imported"
        },
        "questions": questions
    }

def import_file_to_db(filepath):
    if not os.path.exists(filepath):
        print(f"[LỖI] Không tìm thấy file: {filepath}")
        return False

    init_db()
    
    ext = os.path.splitext(filepath)[1].lower()
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    data = None
    if ext == ".json":
        data = json.loads(content)
    elif ext in [".txt", ".md"]:
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        set_id = f"import_{base_name.lower().replace(' ', '_')}"
        title = base_name.replace("_", " ").title()
        data = parse_txt_exam(content, default_set_id=set_id, default_title=title)
    else:
        print(f"[LỖI] Định dạng file không hỗ trợ: {ext} (Chỉ hỗ trợ .json, .txt, .md)")
        return False

    set_info = data.get("set", {})
    questions = data.get("questions", [])

    if not set_info or not questions:
        print("[LỖI] File không chứa đủ thông tin 'set' hoặc 'questions'")
        return False

    conn = get_connection()
    cursor = conn.cursor()

    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    set_id = set_info.get("id", "custom_set")

    cursor.execute("""
    INSERT OR REPLACE INTO test_sets (id, title, description, category, difficulty, time_limit, badge, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        set_id,
        set_info.get("title", "Đề mới nạp"),
        set_info.get("description", ""),
        set_info.get("category", "Tự nạp"),
        set_info.get("difficulty", "B1"),
        set_info.get("time_limit", 15),
        set_info.get("badge", "Imported"),
        now
    ))

    # Xóa câu hỏi cũ cùng set nếu ghi đè
    cursor.execute("DELETE FROM questions WHERE set_id = ?", (set_id,))

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

    print("=======================================================")
    print(f"🎉 NẠP THÀNH CÔNG BỘ ĐỀ: {set_info.get('title')}")
    print(f"📝 Số lượng câu hỏi đã thêm: {added_count} câu")
    print(f"⏱️ Thời gian làm bài: {set_info.get('time_limit', 15)} phút")
    print(f"🌐 Bộ đề đã sẵn sàng trong ứng dụng tại mục 'Kho Đề'!")
    print("=======================================================")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nCách sử dụng công cụ nạp đề:")
        print("  python import_tool.py <đường_dẫn_file_json_hoặc_txt>")
        print("Ví dụ:")
        print("  python import_tool.py sample_data/de_thi_mau.json")
        print("  python import_tool.py sample_data/de_thi_mau.txt\n")
    else:
        import_file_to_db(sys.argv[1])
