from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.upload_api import router as upload_router
from app.api.transcribe_api import router as transcribe_router
from app.api.download_api import router as download_router
from app.api.status_api import router as status_router

app = FastAPI()  # ← 必須！

app.include_router(upload_router)
app.include_router(transcribe_router)
app.include_router(download_router)
app.include_router(status_router)

# CORSの設定（Reactとの連携を想定）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
