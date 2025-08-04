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
    minify: 'terser',
    // Rollupのネイティブモジュールを無効化
    commonjsOptions: {
      include: []
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom'],
    exclude: ['@rollup/rollup-linux-x64-gnu']
  },
  server: {
    host: '0.0.0.0',
    port: 3000
  },
  // 開発時の設定
  define: {
    global: 'globalThis'
  }
})
