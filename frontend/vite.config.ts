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
    minify: 'terser'
  },
  optimizeDeps: {
    include: ['react', 'react-dom']
  },
  server: {
    host: '0.0.0.0',
    port: 3000
  }
})
