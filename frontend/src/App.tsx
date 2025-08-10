import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [transcription, setTranscription] = useState("ここに結果が表示されます");
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<string>("未確認");

  // APIベースURLを計算する関数
  const getApiBaseUrl = () => {
    // 環境変数から取得
    const envBase = import.meta.env.VITE_API_BASE;
    console.log('環境変数 VITE_API_BASE:', envBase);
    
    if (envBase && envBase.trim() !== '') {
      return envBase.replace(/\/$/, '');
    }
    
    // フォールバック: 本番環境では現在のドメインを使用
    if (import.meta.env.PROD) {
      const currentOrigin = window.location.origin;
      console.log('現在のオリジン:', currentOrigin);
      return currentOrigin;
    }
    
    // 開発環境では localhost
    return 'http://localhost:8000';
  };

  const checkApiHealth = async () => {
    try {
      const base = getApiBaseUrl();
      const healthUrl = `${base}/api/health`;
      const rootUrl = `${base}/`;

      console.log('ヘルスチェック呼び出し:', healthUrl);
      console.log('ルートパス確認:', rootUrl);
      console.log('環境変数 VITE_API_BASE:', import.meta.env.VITE_API_BASE);
      console.log('環境変数 PROD:', import.meta.env.PROD);
      console.log('計算されたベースURL:', base);

      // まずルートパスを試行
      try {
        const rootResponse = await fetch(rootUrl);
        console.log('ルートパスレスポンス:', rootResponse.status, rootResponse.statusText);
        if (rootResponse.ok) {
          const rootData = await rootResponse.text();
          console.log('ルートパスデータ（先頭100文字）:', rootData.substring(0, 100));
        }
      } catch (rootError) {
        console.log('ルートパスエラー:', rootError);
      }

      const response = await fetch(healthUrl);
      console.log('ヘルスチェックレスポンスステータス:', response.status);
      console.log('レスポンスヘッダー:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('APIエラーレスポンス:', errorText);
        setApiStatus(`接続エラー: ${response.status} ${response.statusText}`);
        return;
      }

      const data = await response.json();

      if (response.ok && data.status === 'ok') {
        setApiStatus('接続OK');
        console.log('API接続正常:', data);
      } else {
        setApiStatus(`接続エラー: ${response.status}`);
        console.error('API接続エラー:', response.status, data);
      }
    } catch (error) {
      setApiStatus('接続失敗');
      console.error('ヘルスチェックエラー:', error);

      // エラーの詳細を表示
      if (error instanceof Error) {
        console.error('エラーメッセージ:', error.message);
        console.error('エラースタック:', error.stack);
      }
    }
  };

  // コンポーネントマウント時にヘルスチェック
  useEffect(() => {
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

      console.log('API呼び出し:', apiUrl);

      const response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });

      console.log('レスポンスステータス:', response.status);
      console.log('レスポンスヘッダー:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('APIエラーレスポンス:', errorText);
        throw new Error(`APIリクエスト失敗: ${response.status} ${response.statusText}`);
      }

      const responseText = await response.text();
      console.log('レスポンス内容:', responseText);

      if (!responseText || responseText.trim() === '') {
        throw new Error('APIから空のレスポンスが返されました');
      }

      let data;
      try {
        data = JSON.parse(responseText);
      } catch (parseError) {
        console.error('JSONパースエラー:', parseError);
        console.error('パース対象テキスト:', responseText);
        throw new Error('APIレスポンスのJSONパースに失敗しました');
      }

      if (!data || typeof data !== 'object') {
        throw new Error('APIレスポンスが不正な形式です');
      }

      setTranscription(data.transcription || "文字起こしに失敗しました");
    } catch (error) {
      console.error("エラー詳細:", error);
      setTranscription(`エラーが発生しました: ${error instanceof Error ? error.message : '不明なエラー'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = (format: "txt" | "json") => {
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

  return (
    <div className="app-container">
      <h1 className="app-title">Whisper Transcriber</h1>

      {/* APIステータス表示 */}
      <div className="api-status">
        <span>API接続状態: {apiStatus}</span>
        <button
          onClick={checkApiHealth}
          className="health-check-button"
          disabled={isLoading}
        >
          接続確認
        </button>
      </div>

      <div className="upload-section">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
          accept="audio/*,.mp3,.wav,.m4a,.flac"
          disabled={isLoading}
        />
        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={isLoading || !file}
        >
          {isLoading ? '処理中...' : 'アップロードして文字起こし'}
        </button>
      </div>

      <div className="result-container">
        <h2 className="result-title">文字起こし結果</h2>
        <textarea
          className="result-text"
          rows={10}
          cols={40}
          readOnly
          value={transcription}
          placeholder={isLoading ? '処理中...' : 'ここに結果が表示されます'}
        />
        <div className="download-buttons">
          <button
            className="download-button"
            onClick={() => handleDownload("txt")}
            disabled={transcription === "ここに結果が表示されます" || transcription.startsWith("エラー")}
          >
            .txtとしてダウンロード
          </button>
          <button
            className="download-button"
            onClick={() => handleDownload("json")}
            disabled={transcription === "ここに結果が表示されます" || transcription.startsWith("エラー")}
          >
            .jsonとしてダウンロード
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;