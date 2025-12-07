import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://f6094542f541.ngrok-free.app',
        changeOrigin: true,
      },
      '/result': {
        target: 'https://f6094542f541.ngrok-free.app',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'https://f6094542f541.ngrok-free.app',
        changeOrigin: true,
      }
    }
  }
})
