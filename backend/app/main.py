import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# APIルーターをインポート
# (app/api/transcribe_api.py などが存在することを前提としています)
from app.api import transcribe_api, upload_api, health_api, result_api, status_api, download_api

app = FastAPI(title="Whisper Transcribe API", version="1.0.0")

# --- CORS設定の修正 ---
# 許可するオリジン（フロントエンドのURL）を指定
# エラー画像に表示されていたオリジンと、既存のオリジン、ローカル開発用を追加
origins = [
    "https://whisper-transcribe-mdxo.onrender.com",  # ★ エラー画像に表示されていたフロントエンドURL
    "https://whisper-transcribe-m6xq.onrender.com",  # 既存の設定（念のため残す）
    "http://localhost:3000",                        # ローカル開発用 (React)
    "http://127.0.0.1:3000",                      # ローカル開発用 (React)
]
# --- ここまで修正 ---


# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル配信（フロントエンドのビルド結果）
# Render環境では ./static ディレクトリにコピーされている
frontend_build_path = Path("./static")
if frontend_build_path.exists():
    try:
        # 静的ファイルを /static にマウント（正しいMIMEタイプで配信）
        app.mount("/static", StaticFiles(directory=str(frontend_build_path), html=True), name="static")
        print(f"静的ファイル配信を有効化: {frontend_build_path} -> /static")
        
        # 静的ファイルの内容を確認
        static_files = list(frontend_build_path.rglob("*"))
        print(f"静的ファイル数: {len(static_files)}")
        for file in static_files[:5]:  # 最初の5ファイルを表示
            print(f"  - {file}")
    except Exception as e:
        print(f"静的ファイル配信の設定エラー: {e}")
else:
    print(f"警告: フロントエンドビルドディレクトリが見つかりません: {frontend_build_path}")
    # フォールバック: 相対パスも試行
    fallback_path = Path("../frontend/dist")
    if fallback_path.exists():
        try:
            app.mount("/static", StaticFiles(directory=str(fallback_path), html=True), name="static")
            print(f"フォールバック静的ファイル配信を有効化: {fallback_path} -> /static")
        except Exception as e:
            print(f"フォールバック静的ファイル配信の設定エラー: {e}")
    else:
        print(f"フォールバックパスも見つかりません: {fallback_path}")

# APIルーターを追加
app.include_router(transcribe_api.router, prefix="/api", tags=["transcribe"])
app.include_router(upload_api.router, prefix="/api", tags=["upload"])
app.include_router(health_api.router, prefix="/api", tags=["health"])
app.include_router(result_api.router, prefix="/api", tags=["result"])
app.include_router(status_api.router, prefix="/api", tags=["status"])
app.include_router(download_api.router, prefix="/api", tags=["download"])

@app.get("/health")
async def health_check():
    """APIサーバー自体のヘルスチェック"""
    return {"status": "ok", "message": "Whisper Transcribe API is running"}

@app.get("/api/health")
async def api_health_check():
    """APIエンドポイントのヘルスチェック（/api プレフィックス）"""
    return {"status": "ok", "message": "API endpoints are available"}

@app.get("/test-static")
async def test_static():
    """静的ファイルの配信状況をテストするエンドポイント"""
    frontend_build_path = Path("./static")
    
    if not frontend_build_path.exists():
        return {"error": "Static directory not found", "path": str(frontend_build_path.resolve())}
    
    # 静的ファイルの一覧を取得
    static_files = list(frontend_build_path.rglob("*"))
    file_info = []
    
    for file_path in static_files:
        if file_path.is_file():
            try:
                stat = file_path.stat()
                file_info.append({
                    "path": str(file_path.relative_to(frontend_build_path)),
                    "size": stat.st_size,
                    "exists": True
                })
            except Exception as e:
                file_info.append({
                    "path": str(file_path.relative_to(frontend_build_path)),
                    "error": str(e)
                })
    
    return {
        "static_directory": str(frontend_build_path.resolve()),
        "exists": frontend_build_path.exists(),
        "files": file_info,
        "total_files": len(file_info)
    }

@app.get("/")
async def root():
    """ルートパス: フロントエンドのindex.htmlを返す"""
    frontend_build_path = Path("./static")
    index_path = frontend_build_path / "index.html"
    
    print(f"ルートパスアクセス: index.htmlを探しています")
    print(f"探しているパス: {index_path.resolve()}")
    
    if index_path.exists():
        print(f"index.htmlが見つかりました: {index_path}")
        return FileResponse(str(index_path), media_type="text/html")
    
    # フォールバック
    fallback_path = Path("../frontend/dist/index.html")
    print(f"フォールバックパスを確認: {fallback_path.resolve()}")
    if fallback_path.exists():
        print(f"フォールバックindex.htmlが見つかりました: {fallback_path}")
        return FileResponse(str(fallback_path), media_type="text/html")
    
    # 静的ファイルディレクトリの内容を確認
    if frontend_build_path.exists():
        static_files = list(frontend_build_path.rglob("*"))
        print(f"静的ファイルディレクトリの内容:")
        for file in static_files[:10]:
            print(f"  - {file}")
    
    # 最後のフォールバック: API情報を返す
    return {"message": "Whisper Transcribe API", "version": "1.0.0", "status": "frontend_not_found", "error": f"index.html not found at {index_path.resolve()}"}

@app.get("/{full_path:path}")
async def spa(full_path: str):
    """SPAフォールバック: 静的ファイルが見つからない場合にindex.htmlを返す"""
    frontend_build_path = Path("./static")
    static_file_path = frontend_build_path / full_path
    
    # APIパス（/api）やマウント済みのパス（/static）、ヘルスチェックパスは除外
    if (full_path.startswith("api/") or 
        full_path.startswith("static/") or 
        full_path == "health" or 
        full_path == "test-static"):
         # このリクエストはSPAの対象外であるため、FastAPIの次の処理（または404）に任せる
         # ここでエラーを返さず、他のルートにマッチする可能性を残す
         # ただし、これが最後のルートなので、事実上404 Not Foundとなる
         return {"error": "Not a SPA path", "path": full_path}

    # 静的ファイルが具体的に存在する場合はStaticFilesが処理するはず
    # ここに到達するのは、React Routerが処理すべきパス
    if static_file_path.exists() and static_file_path.is_file():
        pass

    # その他のパスではindex.htmlを返す（SPAルーティング）
    index_path = frontend_build_path / "index.html"
    print(f"SPAフォールバック: {full_path} -> index.html")
    
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    
    # フォールバック
    fallback_path = Path("../frontend/dist/index.html")
    if fallback_path.exists():
        return FileResponse(str(fallback_path), media_type="text/html")
    
    print(f"SPAフォールバックエラー: index.htmlが見つかりません。 path: {full_path}")
    return {"error": "Frontend not found", "path": full_path}

if __name__ == "__main__":
    import uvicorn
    # PORT環境変数を読み込む（RenderなどのPaaS対応）
    port = int(os.getenv("PORT", 8000))
    # 0.0.0.0 を指定して、コンテナ外部からのアクセスを受け入れる
    # "main:app" のように文字列で指定し、reload=Trueで開発時に自動リロード
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
