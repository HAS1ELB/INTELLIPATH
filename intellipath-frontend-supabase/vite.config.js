import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/', // Root path for Netlify
  build: {
    outDir: 'dist', // Default output directory
    assetsDir: 'assets', // Default assets directory
    sourcemap: false // Disable sourcemaps for production
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})