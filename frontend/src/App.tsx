import { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [transcription, setTranscription] = useState("ここに結果が表示されます");

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      // 別ドメインのバックエンドに対応: VITE_API_BASE を優先
      const rawBase = (import.meta.env.VITE_API_BASE as string | undefined) || (import.meta.env.PROD ? '' : 'http://localhost:8000');
      const base = rawBase.replace(/\/$/, ''); // 末尾スラッシュを除去
      const apiUrl = `${base}/api/transcribe`;
      
      const response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("APIリクエスト失敗");
      }

      const data = await response.json();
      setTranscription(data.transcription || "文字起こしに失敗しました");
    } catch (error) {
      console.error("エラー:", error);
      setTranscription("エラーが発生しました");
    }
  };

  const handleDownload = (ext: "txt" | "json") => {
    const blob = new Blob(
      [ext === "json" ? JSON.stringify({ transcription }, null, 2) : transcription],
      { type: "text/plain" }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transcription.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app-container">
      <h1 className="app-title">Whisper Transcriber</h1>
      <div className="upload-section">
        <input type="file" onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)} />
        <button className="upload-button" onClick={handleUpload}>アップロードして文字起こし</button>
      </div>
      <div className="result-container">
        <div className="result-title">文字起こし結果：</div>
        <textarea className="result-text" rows={10} cols={40} readOnly value={transcription} />
        <div className="download-buttons">
          <button className="download-button" onClick={() => handleDownload("txt")}>.txtとしてダウンロード</button>
          <button className="download-button" onClick={() => handleDownload("json")}>.jsonとしてダウンロード</button>
        </div>
      </div>
    </div>
  );
}

export default App;