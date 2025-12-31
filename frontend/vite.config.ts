import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: [
      'frontend', // Docker hostname
      'localhost', // Local development
      '127.0.0.1', // Local development
      '.localhost', // Localhost subdomains
    ],
    // Alternatively, you can use 'all' to allow all hosts (less secure)
    // allowedHosts: 'all',
  },
})
