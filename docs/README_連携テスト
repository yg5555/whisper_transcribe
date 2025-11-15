## 🚀 ローカル環境での連携テスト手順

本番環境（Renderなど）へのデプロイ前に、ローカルPC上でフロントエンド（React）とバックエンド（FastAPI）を同時に起動し、APIの連携とCORS設定が正しいかを確認する手順です。

* **バックエンド (FastAPI):** `http://localhost:8000` で実行
* **フロントエンド (React):** `http://localhost:3000` で実行

---

### 1. バックエンド (FastAPI) の起動

まず、APIサーバーを起動します。

1.  **ターミナル（1つ目）** を開きます。
2.  バックエンドのプロジェクトディレクトリ（`main.py` がある場所）に移動します。
3.  以下のコマンドを実行し、FastAPIサーバーを起動します。

    ```bash
    uvicorn main:app --reload --port 8000
    ```

4.  ターミナルに `Application startup complete.` と表示され、`http://127.0.0.1:8000` で待機状態になったことを確認します。（このターミナルは起動したままにします）

---

### 2. フロントエンド (React) の設定確認

次に、Reactアプリがローカルのバックエンド（`:8000`）を見にいく設定になっているか確認します。

1.  Reactプロジェクトのコードを開きます。
2.  APIのベースURLを定義しているファイル（`.env.development` や `src/api/config.js` など）を確認します。
3.  開発環境用のAPI URLが、`http://localhost:8000` になっていることを確認します。

    **▼ 設定例 (`.env.development`)**
    ```
    REACT_APP_API_BASE_URL=http://localhost:8000
    ```

    ※もし本番URL（`https://...onrender.com`）になっていた場合は、テストのために一時的に上記に変更してください。

---

### 3. フロントエンド (React) の起動

APIサーバーとは**別のターミナル**でReactの開発サーバーを起動します。

1.  **ターミナル（2つ目）** を開きます。
2.  フロントエンドのプロジェクトディレクトリに移動します。
3.  以下のコマンドを実行して、Reactアプリを起動します。

    ```bash
    npm start
    ```
    *(または `yarn start`)*

4.  自動的にブラウザが起動し、`http://localhost:3000` でアプリの画面が表示されます。

---

### 4. 動作確認と合格基準

`http://localhost:3000` が開かれているブラウザで、以下の方法でエラーが出ていないか確認します。

1.  ブラウザの開発者ツールを開きます。（Mac: `Cmd` + `Opt` + `I`, Windows: `Ctrl` + `Shift` + `I`）
2.  「**Console (コンソール)**」タブを開きます。
3.  アプリの操作（ファイルアップロードなど）を行います。

**✅ テスト成功の基準:**
* 「**Console**」タブに **CORS関連のエラー (`Access-Control-Allow-Origin`...) が一切表示されない**こと。
* 「**Network (ネットワーク)**」タブで、`upload` や `transcribe` などのAPI通信（`localhost:8000` 宛）のステータスが `200 OK` になっていること。