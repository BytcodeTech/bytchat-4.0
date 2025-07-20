import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom'; // <-- 1. Importamos useLocation
import { BotMessageSquare, BrainCircuit, BarChart3, CreditCard, LogOut, Settings, CodeXml, Shield, DollarSign } from 'lucide-react';
import NavButton from '@/components/ui/NavButton';
import { useAuthStore } from '@/store/authStore'; // <-- 2. Importamos el store
import { Icons } from '@/components/ui/icons';
import LogoBytcodeAnimated from '@/components/ui/LogoBytcodeAnimated';

interface SidebarProps {
  className?: string;
  onClose?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ className = '', onClose }) => {
  // --- 3. Preparamos la lógica de logout ---
  const { logout, isAdmin } = useAuthStore();
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
      <div className="p-6 flex flex-col items-center space-y-2 border-b border-slate-700">
        <LogoBytcodeAnimated onlyA className="w-[85px] h-[85px]" />
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
        <NavButton 
          icon={BarChart3} 
          label="Analíticas" 
          isActive={pathname.startsWith('/analytics')}
          onClick={() => navigate('/analytics')}
        />
        <NavButton 
          icon={CreditCard} 
          label="Facturación" 
          isActive={pathname.startsWith('/billing')}
          onClick={() => navigate('/billing')}
        />
        
        {/* Panel de Administración - Solo para administradores */}
        {isAdmin() && (
          <>
            <NavButton
              icon={Shield}
              label="Panel de Administración"
              isActive={pathname.startsWith('/admin')}
              onClick={() => navigate('/admin')}
            />
            <NavButton
              icon={DollarSign}
              label="Gestión de Precios"
              isActive={pathname.startsWith('/model-pricing')}
              onClick={() => navigate('/model-pricing')}
            />
          </>
        )}
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