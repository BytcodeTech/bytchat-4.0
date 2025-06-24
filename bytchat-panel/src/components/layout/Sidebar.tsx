import { BotMessageSquare, BrainCircuit, BarChart3, CreditCard, LogOut, Settings } from 'lucide-react';
import NavButton from '@/components/ui/NavButton';

const Sidebar = () => {
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
        <NavButton icon={BotMessageSquare} label="Mis Bots" isActive />
        <NavButton icon={BrainCircuit} label="Entrenamiento" />
        <NavButton icon={BarChart3} label="Analíticas" />
        <NavButton icon={CreditCard} label="Facturación" />
      </nav>

      {/* --- Footer Navigation --- */}
      <div className="p-4 border-t border-slate-700">
        <NavButton icon={Settings} label="Configuración" />
        <NavButton icon={LogOut} label="Cerrar Sesión" />
      </div>
    </aside>
  );
};

export default Sidebar;