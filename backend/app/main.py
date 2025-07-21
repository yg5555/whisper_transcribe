from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORSミドルウェア追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React の開発サーバーのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 以下は既存のルーティング設定
from app.api import transcribe_api
app.include_router(transcribe_api.router)