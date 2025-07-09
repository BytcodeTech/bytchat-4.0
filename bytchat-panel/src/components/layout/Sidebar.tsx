import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom'; // <-- 1. Importamos useLocation
import { BotMessageSquare, BrainCircuit, BarChart3, CreditCard, LogOut, Settings, CodeXml } from 'lucide-react';
import NavButton from '@/components/ui/NavButton';
import { useAuthStore } from '@/store/authStore'; // <-- 2. Importamos el store

interface SidebarProps {
  className?: string;
  onClose?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ className = '', onClose }) => {
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
    <aside className={`flex flex-col w-64 bg-slate-800 text-white relative ${className}`}>
      {/* Botón cerrar solo en móvil */}
      {onClose && (
        <button
          className="absolute top-4 right-4 md:hidden text-white text-2xl"
          onClick={onClose}
        >
          ×
        </button>
      )}
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
        <NavButton
          icon={CodeXml}
          label="Incrustar Chat"
          isActive={pathname.startsWith('/embed-chat')}
          onClick={() => navigate('/embed-chat')}
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