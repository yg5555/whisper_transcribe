import React from 'react';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <h1 className="app-title">Whisper Transcriber</h1>
      <div className="upload-section">
        <input type="file" />
        <button className="upload-button">アップロードして文字起こし</button>
      </div>
      <div className="result-container">
        <div className="result-title">文字起こし結果：</div>
        <textarea className="result-text" rows={10} cols={40} readOnly value={"ここに結果が表示されます"} />
        <div className="download-buttons">
          <button className="download-button">.txtとしてダウンロード</button>
          <button className="download-button">.jsonとしてダウンロード</button>
        </div>
      </div>
    </div>
  );
}

export default App;
