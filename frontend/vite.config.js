import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // Use 8001 if port 8000 is occupied by another process
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
})
