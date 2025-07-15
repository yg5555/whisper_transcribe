import { useState } from 'react'
import axios from 'axios'

const FileUploader = () => {
  const [file, setFile] = useState<File | null>(null)
  const [status, setStatus] = useState('')

  const handleUpload = async () => {
    if (!file) {
      setStatus('ファイルを選択してください')
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)

      // アップロード
      await axios.post('http://localhost:8000/api/upload', formData)
      setStatus('アップロード完了 → 文字起こし開始中...')

      // 文字起こし実行
      await axios.post('http://localhost:8000/api/transcribe', {
        filename: file.name,
      })
      setStatus('文字起こし完了')
    } catch (error) {
      setStatus('エラーが発生しました')
      console.error(error)
    }
  }

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', marginTop: '20px' }}>
      <input
        type="file"
        accept=".mp3,.wav,.m4a"
        onChange={(e) => {
          if (e.target.files?.[0]) setFile(e.target.files[0])
        }}
      />
      <button onClick={handleUpload}>アップロードして変換</button>
      <p>{status}</p>
    </div>
  )
}

export default FileUploader