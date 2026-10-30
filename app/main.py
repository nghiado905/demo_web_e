import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes import router
from app.database import init_db
from app.data_seeder import seed_database

app = FastAPI(
    title="EnglishMaster Quiz Pro",
    description="Ứng dụng luyện thi và giải đề trắc nghiệm tiếng Anh cục bộ",
    version="1.0.0"
)

# Startup event: Initialize DB and seed initial data if empty
@app.on_event("startup")
def on_startup():
    init_db()
    seed_database()

# Include API routes
app.include_router(router)

# Mount static folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Quiz App Backend is Running. Index file not found."}
