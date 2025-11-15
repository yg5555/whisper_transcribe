# 1. ベースにするOSイメージを指定
FROM python:3.10-slim

# 2. アプリのコードを置く場所（作業ディレクトリ）を指定
WORKDIR /app

# 3. 必要なライブラリをインストールするための準備
#    (requirements.txt を先にコピーする)
COPY requirements.txt .

# 4. requirements.txt に書かれたライブラリをインストール
RUN pip install -r requirements.txt

# 5. アプリのコード一式をコピー
COPY . .

# 6. アプリを実行するコマンドを指定
#    (Hugging Face Spacesは $PORT 環境変数でポートを指定します)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]