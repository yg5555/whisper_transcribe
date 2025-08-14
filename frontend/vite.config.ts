import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 環境変数を読み込み
  const env = loadEnv(mode, resolve(__dirname), '')
  
  return {
    plugins: [react()],
    // Rollupを無効化してesbuildのみを使用
    build: {
      target: 'es2015',
      chunkSizeWarningLimit: 1000,
      sourcemap: false,
      minify: 'esbuild',
      rollupOptions: {
        // Rollupを無効化
        external: () => false,
        output: {
          manualChunks: undefined
        }
      }
    },
    // 本番環境では /static パスを使用
    base: mode === 'production' ? '/static/' : '/',
    optimizeDeps: {
      include: ['react', 'react-dom']
    },
    server: {
      host: '0.0.0.0',
      port: 3000
    },
    // 開発時の設定
    define: {
      global: 'globalThis',
      // ビルド時に環境変数を注入
      'import.meta.env.VITE_API_BASE': JSON.stringify(env.VITE_API_BASE || ''),
      'import.meta.env.PROD': JSON.stringify(mode === 'production')
    },
    // メモリ効率化
    esbuild: {
      target: 'es2015'
    }
  }
})
