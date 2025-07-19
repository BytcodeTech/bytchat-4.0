import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tsconfigPaths()
  ],
  
  server: {
    proxy: {
      '/api': {
        target: 'http://161.132.45.210:8001',
        changeOrigin: true,
        // Volvemos a añadir la regla "rewrite"
        rewrite: (path) => path.replace(/^\/api/, ''),
      }
    },
    host: '0.0.0.0',
    port: 5176,
    strictPort: true,
  }
})