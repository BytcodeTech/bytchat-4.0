import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths' // <--- 1. Importar el plugin

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tsconfigPaths()], // <--- 2. Añadir el plugin aquí
})