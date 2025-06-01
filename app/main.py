from fastapi import FastAPI
from app.upload_api import router

app = FastAPI()
app.include_router(router)

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}