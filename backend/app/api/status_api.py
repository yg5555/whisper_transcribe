from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

# 仮のステータス確認エンドポイント
@router.get("/status/{file_id}")
async def get_status(file_id: str):
    # 実際の処理では、file_id に対応するステータス管理ロジックをここに実装する
    return JSONResponse(content={"file_id": file_id, "status": "processing"}, status_code=200)
