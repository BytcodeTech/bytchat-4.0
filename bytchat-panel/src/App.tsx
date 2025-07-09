// bytchat-panel/src/App.tsx
import { useEffect, useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import { Toaster } from 'sonner'; // <-- 1. IMPORTAR TOASTER

function App() {
  const { token, checkAuth } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Bloquear scroll del body cuando el sidebar está abierto en móvil
  useEffect(() => {
    if (sidebarOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [sidebarOpen]);

  useEffect(() => {
    checkAuth();
    if (!token) {
      navigate('/login');
    }
  }, [token, navigate, checkAuth]);

  if (!token) {
    return null; 
  }

  const isDashboard = location.pathname === '/dashboard';

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar para escritorio */}
      <Sidebar className="hidden md:flex" />
      {/* Sidebar para móvil con overlay */}
      {sidebarOpen && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 z-40 bg-black bg-opacity-40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
          {/* Sidebar */}
          <Sidebar 
            className="fixed inset-0 z-50 flex md:hidden bg-slate-800/95" 
            onClose={() => setSidebarOpen(false)} 
          />
        </>
      )}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
      {/* 2. AÑADIR EL COMPONENTE TOASTER AQUÍ */}
      <Toaster richColors position="top-right" />
    </div>
  );
}

export default App;