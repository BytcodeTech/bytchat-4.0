import { useNavigate, useLocation } from 'react-router-dom'; // <-- 1. Importamos useLocation
import { BotMessageSquare, BrainCircuit, BarChart3, CreditCard, LogOut, Settings } from 'lucide-react';
import NavButton from '@/components/ui/NavButton';
import { useAuthStore } from '@/store/authStore'; // <-- 2. Importamos el store

const Sidebar = () => {
  // --- 3. Preparamos la lógica de logout ---
  const { logout } = useAuthStore();
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  // ------------------------------------

  return (
    <aside className="hidden md:flex flex-col w-64 bg-slate-800 text-white">
      {/* --- Logo Header --- */}
      <div className="p-6 flex items-center space-x-3 border-b border-slate-700">
        <div className="w-10 h-10 bg-sky-600 rounded-lg flex items-center justify-center font-bold text-xl">
          B
        </div>
        <h1 className="text-xl font-bold">Bytchat Panel</h1>
      </div>

      {/* --- Main Navigation --- */}
      <nav className="flex-1 p-4 space-y-2">
        <NavButton
          icon={BotMessageSquare}
          label="Mis Bots"
          isActive={pathname.startsWith('/bots') || pathname === '/'}
          onClick={() => navigate('/bots')}
        />
        <NavButton
          icon={BrainCircuit}
          label="Entrenamiento"
          isActive={pathname.startsWith('/training')}
          onClick={() => navigate('/training')}
        />
        <NavButton icon={BarChart3} label="Analíticas" />
        <NavButton icon={CreditCard} label="Facturación" />
      </nav>

      {/* --- Footer Navigation --- */}
      <div className="p-4 border-t border-slate-700 space-y-2">
        <NavButton icon={Settings} label="Configuración" />
        {/* --- 4. Aplicamos el onClick al botón correcto --- */}
        <NavButton icon={LogOut} label="Cerrar Sesión" onClick={handleLogout} />
      </div>
    </aside>
  );
};

export default Sidebar;