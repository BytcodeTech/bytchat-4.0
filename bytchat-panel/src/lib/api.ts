// bytchat-panel/src/lib/api.ts
import { useAuthStore } from '@/store/authStore';
import axios from 'axios';

// --- CAMBIO PRINCIPAL ---
// En lugar de una URL completa, usamos una ruta relativa.
// Esto le dice a Axios que haga la solicitud al mismo host y puerto
// donde se ejecuta Vite. Vite verá que la ruta empieza por '/api'
// y la redirigirá a http://127.0.0.1:8001 como se define en vite.config.ts
const API_URL = '/api'; 

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// El interceptor para el token se mantiene igual, es correcto.
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;