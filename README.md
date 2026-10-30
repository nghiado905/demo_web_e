# 🎯 EnglishMaster Quiz Pro (Local Python App)

Ứng dụng luyện thi và giải đề trắc nghiệm tiếng Anh cục bộ (100% offline, lưu trữ bằng SQLite), giao diện web hiện đại, hỗ trợ phát âm bản ngữ và giải thích chi tiết ngữ pháp bằng tiếng Việt.

---

## 🌟 Tính Năng Nổi Bật

1. **Chế Độ Luyện Tập (Practice Mode)**:
   - Làm bài theo tốc độ riêng.
   - Chọn đáp án có phản hồi đúng/sai ngay lập tức.
   - **Phát âm bản xứ**: Nút 🔊 nghe đọc cả câu với Web Speech API (US/UK).
   - **Giải thích chuyên sâu**: Dịch nghĩa toàn bộ câu, phân tích ngữ pháp vì sao đúng/sai, danh sách từ vựng trọng tâm.

2. **Chế Độ Thi Thử (Exam Mode)**:
   - Đồng hồ đếm ngược (Countdown Timer) theo thời gian chuẩn của đề thi.
   - Question Navigator Palette: Bảng số câu (1 đến N) hiển thị trạng thái (Đã làm, Chưa làm, Gắn cờ xem lại 🚩).
   - Tính điểm % và quy đổi ước tính thang điểm **TOEIC Reading**.
   - Bảng tổng kết kết quả với biểu đồ tròn động và phân tích câu sai.

3. **Sổ Tay Câu Hỏi Sai (Mistake Notebook - Spaced Repetition)**:
   - Mọi câu bạn làm sai trong các lần thi hoặc luyện tập sẽ được **tự động lưu vào Sổ tay câu sai**.
   - Có nút **"Ôn tập ngay các câu sai"** để tạo ngay bài luyện tập riêng cho điểm yếu của bạn.
   - Khi làm đúng hoặc hiểu bài, bạn có thể bấm **"Đã thành thạo"** để đưa ra khỏi danh sách.

4. **Sổ Tay Câu Hỏi Quan Tâm (Bookmarks ⭐)**:
   - Lưu lại những câu hỏi ngữ pháp hay hoặc từ vựng khó để ôn lại bất cứ khi nào.

5. **Lịch Sử & Thống Kê (Analytics)**:
   - Lưu trữ nhật ký tất cả các bài thi đã làm trong database SQLite.
   - Thống kê tỷ lệ chính xác %, tổng thời gian học, và nút **"Xem lại"** chi tiết từng câu của các bài thi quá khứ.

6. **Tự Tạo Đề & Nhập Đề JSON (Custom Sets & Import)**:
   - Form thêm câu hỏi trực quan vào từng bộ đề.
   - Công cụ nhập đề bằng mã JSON hàng loạt (có sẵn nút bấm dán mẫu định dạng).

7. **Trải Nghiệm Tối Đa**:
   - Phím tắt bàn phím: Bấm phím **A, B, C, D** (hoặc **1, 2, 3, 4**) để chọn nhanh đáp án, mũi tên **← / →** để chuyển câu, phím **F** để gắn cờ.
   - Chế độ Giao diện **Sáng / Tối (Light / Dark Mode)**.
   - Âm thanh hiệu ứng (Sound Effects) có thể bật/tắt.

---

## 🚀 Cách Khởi Động Ứng Dụng

### Cách 1: Click đúp vào file `run.bat`
Trong thư mục `quizz_local`, chỉ cần click đúp vào file `run.bat`. Trình duyệt sẽ tự động mở trang web ứng dụng tại địa chỉ `http://127.0.0.1:8000`.

### Cách 2: Chạy qua dòng lệnh Terminal
```bash
python main.py
```

Khi server khởi động, ứng dụng sẽ tự động kích hoạt trình duyệt mặc định của bạn. Nếu không tự mở, hãy truy cập:
👉 **http://localhost:8000**

---

## 📁 Cấu Trúc Dự Án

```
quizz_local/
├── app/
│   ├── database.py       # Khởi tạo SQLite, lưu lịch sử, sổ tay câu sai, bookmarks
│   ├── data_seeder.py    # Kho đề mẫu phong phú (TOEIC, Ngữ pháp, Từ vựng)
│   ├── routes.py         # REST API FastAPI (chấm điểm, lấy đề, thống kê)
│   └── main.py           # Thiết lập FastAPI & static router
├── static/
│   ├── css/
│   │   └── style.css     # Giao diện hiện đại, Dark/Light mode, hiệu ứng mượt mà
│   ├── js/
│   │   └── app.js        # Engine giải đề, phát âm, đếm giờ, phím tắt
│   └── index.html        # Giao diện chính Single-Page Application
├── main.py               # File chạy chính + tự động bật trình duyệt
├── run.bat               # File click đúp chạy nhanh trên Windows
├── requirements.txt      # Thư viện phụ thuộc
└── quiz_data.db          # Database SQLite cục bộ (tự tạo khi chạy lần đầu)
```
