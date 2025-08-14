#!/bin/bash

# フロントエンドのフォールバックファイル作成スクリプト
set -e

echo "=== フロントエンドフォールバックファイル作成開始 ==="

# フロントエンドディレクトリに移動
cd frontend

# 既存のdistディレクトリを確認
if [ -d "dist" ]; then
    echo "既存のdistディレクトリが見つかりました"
    ls -la dist/
else
    echo "distディレクトリが見つかりません。作成します。"
    mkdir -p dist/assets
fi

# 基本的なindex.htmlを作成
cat > dist/index.html << 'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/static/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Whisper Transcriber</title>
    <script type="module" crossorigin src="/static/assets/index-BLqfF7NK.js"></script>
    <link rel="stylesheet" crossorigin href="/static/assets/index-aPRTlObn.css">
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
EOF

# 基本的なCSSファイルを作成
cat > dist/assets/index-aPRTlObn.css << 'EOF'
/* 基本的なスタイル */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.app-title {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.upload-section {
  margin-bottom: 30px;
  text-align: center;
}

.upload-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  margin-left: 10px;
}

.upload-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.result-container {
  margin-top: 30px;
}

.result-title {
  color: #333;
  margin-bottom: 15px;
}

.result-text {
  width: 100%;
  min-height: 200px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-family: monospace;
}

.download-buttons {
  margin-top: 15px;
  text-align: center;
}

.download-button {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  margin: 0 5px;
}

.download-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.api-status {
  text-align: center;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 5px;
}

.health-check-button {
  background-color: #17a2b8;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 3px;
  cursor: pointer;
  margin-left: 10px;
}
EOF

# 基本的なJavaScriptファイルを作成（新しいハッシュ名）
cat > dist/assets/index-BLqfF7NK.js << 'EOF'
// 基本的なReactアプリケーション
import React from 'react';
import ReactDOM from 'react-dom/client';

function App() {
  const [file, setFile] = React.useState(null);
  const [transcription, setTranscription] = React.useState("ここに結果が表示されます");
  const [isLoading, setIsLoading] = React.useState(false);
  const [apiStatus, setApiStatus] = React.useState("未確認");

  const getApiBaseUrl = () => {
    const envBase = import.meta.env.VITE_API_BASE;
    if (envBase && envBase.trim() !== '') {
      return envBase.replace(/\/$/, '');
    }
    if (import.meta.env.PROD) {
      return window.location.origin;
    }
    return 'http://localhost:8000';
  };

  const checkApiHealth = async () => {
    try {
      const base = getApiBaseUrl();
      const healthUrl = `${base}/api/health`;
      const response = await fetch(healthUrl);
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'ok') {
          setApiStatus('接続OK');
        } else {
          setApiStatus(`接続エラー: ${response.status}`);
        }
      } else {
        setApiStatus(`接続エラー: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      setApiStatus('接続失敗');
      console.error('ヘルスチェックエラー:', error);
    }
  };

  React.useEffect(() => {
    checkApiHealth();
  }, []);

  const handleUpload = async () => {
    if (!file) return;
    setIsLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const base = getApiBaseUrl();
      const apiUrl = `${base}/api/transcribe`;
      const response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`APIリクエスト失敗: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setTranscription(data.transcription || "文字起こしに失敗しました");
    } catch (error) {
      console.error("エラー詳細:", error);
      setTranscription(`エラーが発生しました: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = (format) => {
    if (transcription === "ここに結果が表示されます" || transcription.startsWith("エラー")) {
      return;
    }

    const content = format === "json" 
      ? JSON.stringify({ transcription }, null, 2)
      : transcription;

    const blob = new Blob([content], { type: format === "json" ? "application/json" : "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transcription.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return React.createElement('div', { className: 'app-container' },
    React.createElement('h1', { className: 'app-title' }, 'Whisper Transcriber'),
    React.createElement('div', { className: 'api-status' },
      React.createElement('span', null, `API接続状態: ${apiStatus}`),
      React.createElement('button', {
        onClick: checkApiHealth,
        className: 'health-check-button',
        disabled: isLoading
      }, '接続確認')
    ),
    React.createElement('div', { className: 'upload-section' },
      React.createElement('input', {
        type: 'file',
        onChange: (e) => setFile(e.target.files ? e.target.files[0] : null),
        accept: 'audio/*,.mp3,.wav,.m4a,.flac',
        disabled: isLoading
      }),
      React.createElement('button', {
        className: 'upload-button',
        onClick: handleUpload,
        disabled: isLoading || !file
      }, isLoading ? '処理中...' : 'アップロードして文字起こし')
    ),
    React.createElement('div', { className: 'result-container' },
      React.createElement('h2', { className: 'result-title' }, '文字起こし結果'),
      React.createElement('textarea', {
        className: 'result-text',
        rows: 10,
        cols: 40,
        readOnly: true,
        value: transcription,
        placeholder: isLoading ? '処理中...' : 'ここに結果が表示されます'
      }),
      React.createElement('div', { className: 'download-buttons' },
        React.createElement('button', {
          className: 'download-button',
          onClick: () => handleDownload("txt"),
          disabled: transcription === "ここに結果が表示されます" || transcription.startsWith("エラー")
        }, '.txtとしてダウンロード'),
        React.createElement('button', {
          className: 'download-button',
          onClick: () => handleDownload("json"),
          disabled: transcription === "ここに結果が表示されます" || transcription.startsWith("エラー")
        }, '.jsonとしてダウンロード')
      )
    )
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(React.createElement(App));
EOF

# vite.svgファイルをコピー
if [ -f "public/vite.svg" ]; then
    cp public/vite.svg dist/
else
    # 基本的なSVGアイコンを作成
    cat > dist/vite.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--logos" width="31.88" height="32" preserveAspectRatio="xMidYMid meet" viewBox="0 0 256 257"><defs><linearGradient id="IconifyId1813088fe1fbc01fb466" x1="-.828%" x2="57.636%" y1="7.652%" y2="78.411%"><stop offset="0%" stop-color="#41D1FF"></stop><stop offset="100%" stop-color="#BD34FE"></stop></linearGradient><linearGradient id="IconifyId1813088fe1fbc01fb467" x1="43.376%" x2="50.316%" y1="2.242%" y2="89.03%"><stop offset="0%" stop-color="#FFEA83"></stop><stop offset="8.333%" stop-color="#FFDD35"></stop><stop offset="100%" stop-color="#FFA800"></stop></linearGradient></defs><path fill="url(#IconifyId1813088fe1fbc01fb466)" d="M255.153 37.938L134.897 252.976c-2.483 4.44-8.862 4.466-11.382.048L.875 37.958c-2.746-4.814 1.371-10.646 6.827-9.67l120.385 21.517a6.537 6.537 0 0 0 2.322-.004l117.867-21.483c5.438-.991 9.574 4.796 6.877 9.62Z"></path><path fill="url(#IconifyId1813088fe1fbc01fb467)" d="M185.432.063L96.44 17.501a3.268 3.268 0 0 0-2.634 3.014l-5.474 92.456a3.268 3.268 0 0 0 3.997 3.378l24.777-5.718c2.318-.535 4.413 1.507 3.936 3.838l-7.361 36.047c-.495 2.426 1.782 4.5 4.151 3.78l15.304-4.649c2.372-.72 4.652 1.36 4.15 3.788l-11.698 56.621c-.732 3.542 3.979 5.473 5.943 2.437l1.313-2.028l72.516-144.72c1.215-2.423-.88-5.186-3.54-4.672l-25.505 4.922c-2.396.462-4.435-1.77-3.759-4.114l16.646-57.705c.677-2.35-1.37-4.583-3.769-4.113Z"></path></svg>
EOF
fi

echo "=== フロントエンドフォールバックファイル作成完了 ==="
echo "作成されたファイル:"
ls -la dist/
