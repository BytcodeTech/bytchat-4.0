import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vitejs.dev/config/
export default defineConfig({
  // Mantenemos los plugins originales de tu proyecto
  plugins: [
    react(),
    tsconfigPaths()
  ],
  
  // Y añadimos la configuración del servidor que faltaba
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        // Esta es la regla clave para que el login y registro funcionen
        rewrite: (path) => path.replace(/^\/api/, ''),
      }
    }
  }
})