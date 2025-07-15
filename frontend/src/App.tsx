import FileUploader from './components/FileUploader'

function App() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <h1>Whisper 文字起こしアプリ</h1>
      <FileUploader />
    </div>
  )
}

export default App
