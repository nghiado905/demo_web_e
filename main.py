import webbrowser
import threading
import time
import uvicorn
from app.main import app

def open_browser():
    """Wait for server to start up then open browser automatically"""
    time.sleep(1.2)
    url = "http://127.0.0.1:8000"
    print(f"\n=======================================================")
    print(f"🚀 EnglishMaster Quiz Pro đã sẵn sàng!")
    print(f"🌐 Đang mở trình duyệt tại: {url}")
    print(f"💡 Nhấn Ctrl + C trong cửa sổ này nếu bạn muốn tắt ứng dụng.")
    print(f"=======================================================\n")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Lưu ý: Không thể tự mở trình duyệt ({e}), hãy mở {url} thủ công.")

if __name__ == "__main__":
    # Start browser opener in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn server
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
