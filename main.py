from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI(
    title="Няш-Форум API",
    description="API для милого форума с сердечками",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Настройки CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Модели данных
class Reply(BaseModel):
    id: str
    author: str
    content: str
    date: str
    hearts: int = 0


class Thread(BaseModel):
    id: str
    title: str
    author: str
    content: str
    date: str
    replies: List[Reply] = []
    hearts: int = 0


# "База данных" в памяти
db = {
    "threads": [
        {
            "id": "1",
            "title": "Какие ваши самые любимые милые аниме?",
            "author": "Сакура",
            "content": "Привет всем! Расскажите о ваших самых любимых милых аниме, которые поднимают настроение! 💖 Я обожаю 'Моя соседка Тоторо' и 'К-ОН!' 😊",
            "date": "2023-05-15",
            "hearts": 5,
            "replies": [
                {
                    "id": "1-1",
                    "author": "Мику",
                    "content": "Ооо, я обожаю 'Сладкая жизнь' и 'Хинаматсу!' 🍡 Они такие милые и уютные! ✨",
                    "date": "2023-05-15",
                    "hearts": 2
                }
            ]
        }
    ]
}


# Вспомогательные функции
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


def generate_id():
    return str(uuid.uuid4())


# Роуты API
@app.get("/api/threads", response_model=List[Thread], tags=["Треды"])
def get_threads():
    """Получить список всех тредов"""
    return db["threads"]


@app.post("/api/threads", response_model=Thread, tags=["Треды"])
def create_thread(thread: Thread):
    """Создать новый тред"""
    thread.id = generate_id()
    thread.date = get_current_date()
    thread.replies = []
    db["threads"].insert(0, thread.dict())
    return thread


@app.get("/api/threads/{thread_id}", response_model=Thread, tags=["Треды"])
def get_thread(thread_id: str):
    """Получить тред по ID"""
    for thread in db["threads"]:
        if thread["id"] == thread_id:
            return thread
    raise HTTPException(status_code=404, detail="Тред не найден")


@app.post("/api/threads/{thread_id}/replies", response_model=Reply, tags=["Ответы"])
def create_reply(thread_id: str, reply: Reply):
    """Добавить ответ в тред"""
    reply.id = generate_id()
    reply.date = get_current_date()

    for thread in db["threads"]:
        if thread["id"] == thread_id:
            thread["replies"].append(reply.dict())
            return reply

    raise HTTPException(status_code=404, detail="Тред не найден")


@app.post("/api/threads/{thread_id}/hearts", tags=["Реакции"])
def add_heart_to_thread(thread_id: str):
    """Добавить сердечко к треду"""
    for thread in db["threads"]:
        if thread["id"] == thread_id:
            thread["hearts"] += 1
            return {"hearts": thread["hearts"]}

    raise HTTPException(status_code=404, detail="Тред не найден")


@app.post("/api/replies/{reply_id}/hearts", tags=["Реакции"])
def add_heart_to_reply(reply_id: str):
    """Добавить сердечко к ответу"""
    for thread in db["threads"]:
        for reply in thread["replies"]:
            if reply["id"] == reply_id:
                reply["hearts"] += 1
                return {"hearts": reply["hearts"]}

    raise HTTPException(status_code=404, detail="Ответ не найден")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)