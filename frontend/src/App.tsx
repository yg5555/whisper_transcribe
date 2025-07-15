import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [transcript, setTranscript] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/transcribe', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setTranscript(data.text);
    } catch (error) {
      console.error('Error:', error);
      setTranscript('エラーが発生しました。');
    }
    setLoading(false);
  };

  const handleDownload = (type: 'txt' | 'json') => {
    const blob = new Blob(
      [type === 'json' ? JSON.stringify({ text: transcript }, null, 2) : transcript],
      { type: type === 'json' ? 'application/json' : 'text/plain' }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcription.${type}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      <h1>Whisper Transcriber</h1>
      <input type="file" accept="audio/*" onChange={handleFileChange} />
      <br /><br />
      <button onClick={handleUpload} disabled={loading || !file}>
        {loading ? '文字起こし中...' : 'アップロードして文字起こし'}
      </button>
      <br /><br />
      {transcript && (
        <div>
          <h3>文字起こし結果：</h3>
          <textarea value={transcript} readOnly style={{ width: '80%', height: '200px' }} />
          <br /><br />
          <button onClick={() => handleDownload('txt')}>.txtとしてダウンロード</button>
          <button onClick={() => handleDownload('json')}>.jsonとしてダウンロード</button>
        </div>
      )}
    </div>
  );
}

export default App;
