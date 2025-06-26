// bytchat-panel/src/App.tsx
import { useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import { Toaster } from 'sonner'; // <-- 1. IMPORTAR TOASTER

function App() {
  const { token, checkAuth } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

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
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
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