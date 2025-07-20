// bytchat-panel/src/lib/api.ts
import axios from 'axios';

// Versión con autenticación restaurada de forma segura
const API_URL = '/api'; 

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor con autenticación lazy (se carga solo cuando se necesita)
api.interceptors.request.use(
  async (config) => {
    try {
      // Importación dinámica para evitar problemas de inicialización
      const { useAuthStore } = await import('@/store/authStore');
      const token = useAuthStore.getState().token;
      
      console.log('🔄 API Request:', config.url, token ? '✅ Con token' : '❌ Sin token');
      
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      return config;
    } catch (error) {
      console.error('❌ Error en interceptor de autenticación:', error);
      return config;
    }
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.message);
    
    // Si es 401, podríamos limpiar el auth store
    if (error.response?.status === 401) {
      console.log('🔑 Error 401: Token inválido o expirado');
    }
    
    return Promise.reject(error);
  }
);

export default api;