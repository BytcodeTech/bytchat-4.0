// bytchat-panel/src/store/authStore.ts

import { create } from 'zustand';

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: true, // Inicia en true para verificar el estado al cargar
  login: (token: string) => {
    localStorage.setItem('token', token);
    set({ token, isAuthenticated: true });
  },
  /**
   * Cierra la sesión del usuario limpiando el token del almacenamiento
   * y actualizando el estado de la aplicación.
   */
  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, isAuthenticated: false });
  },
  /**
   * Verifica si hay un token en el localStorage al iniciar la aplicación
   * para mantener al usuario logueado.
   */
  checkAuth: () => {
    const token = localStorage.getItem('token');
    set({
      token,
      isAuthenticated: !!token,
      isLoading: false, // Termina la carga una vez verificado
    });
  },
}));

// Llamamos a checkAuth al inicio para que el estado se hidrate correctamente
useAuthStore.getState().checkAuth();