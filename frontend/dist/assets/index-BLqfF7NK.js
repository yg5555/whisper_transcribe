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
