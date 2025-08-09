import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      external: [],
      output: {
        manualChunks: undefined
      }
    },
    target: 'es2015',
    // メモリ効率化
    chunkSizeWarningLimit: 1000,
    sourcemap: false
  },
  optimizeDeps: {
    include: ['react', 'react-dom']
  },
  server: {
    host: '0.0.0.0',
    port: 3000
  },
  // 開発時の設定
  define: {
    global: 'globalThis'
  },
  // メモリ効率化
  esbuild: {
    target: 'es2015'
  }
})
