import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    globals: true,
    environment: 'happy-dom',
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['frontend', 'localhost', '127.0.0.1'],
    hmr: {
      host: 'frontend',
      clientPort: 5173,
    },
    watch: {
      usePolling: true,
    },
  },
})
