// bytchat-panel/src/store/authStore.ts

import { create } from 'zustand';

interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_approved: boolean;
  role: 'user' | 'admin' | 'super_admin';
  created_at: string;
  approved_at?: string;
  approved_by?: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  checkAuth: () => void;
  updateUser: (user: User) => void;
  isAdmin: () => boolean;
  isSuperAdmin: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem('token'),
  user: null,
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: true, // Inicia en true para verificar el estado al cargar
  login: (token: string, user: User) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },
  /**
   * Cierra la sesión del usuario limpiando el token del almacenamiento
   * y actualizando el estado de la aplicación.
   */
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ token: null, user: null, isAuthenticated: false });
  },
  /**
   * Verifica si hay un token en el localStorage al iniciar la aplicación
   * para mantener al usuario logueado.
   */
  checkAuth: () => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    
    set({
      token,
      user,
      isAuthenticated: !!token,
      isLoading: false, // Termina la carga una vez verificado
    });
  },
  /**
   * Actualiza la información del usuario en el store
   */
  updateUser: (user: User) => {
    localStorage.setItem('user', JSON.stringify(user));
    set({ user });
  },
  /**
   * Verifica si el usuario actual es administrador
   */
  isAdmin: () => {
    const { user } = get();
    return user?.role === 'admin' || user?.role === 'super_admin';
  },
  /**
   * Verifica si el usuario actual es super administrador
   */
  isSuperAdmin: () => {
    const { user } = get();
    return user?.role === 'super_admin';
  },
}));

// Llamamos a checkAuth al inicio para que el estado se hidrate correctamente
useAuthStore.getState().checkAuth();