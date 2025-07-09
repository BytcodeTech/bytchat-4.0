import { Menu, Search, Bell, CircleUser } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import React from 'react';

interface HeaderProps {
  onMenuClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  return (
    <header className="flex items-center h-16 px-6 border-b bg-white">
      {/* Botón para menú en móvil */}
      <Button variant="ghost" size="icon" className="md:hidden" onClick={onMenuClick}>
        <Menu className="h-6 w-6" />
        <span className="sr-only">Abrir menú</span>
      </Button>

      {/* Barra de búsqueda */}
      <div className="relative flex-1 ml-4 md:ml-0">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
        <Input
          type="search"
          placeholder="Buscar bots o conversaciones..."
          className="w-full max-w-sm pl-10 bg-slate-100 border-none"
        />
      </div>

      <div className="ml-auto flex items-center space-x-4">
        <Button variant="ghost" size="icon">
          <Bell className="h-5 w-5" />
          <span className="sr-only">Notificaciones</span>
        </Button>
        {/* User Avatar - Vuelve a ser solo un placeholder visual */}
        <div className="h-9 w-9 rounded-full bg-slate-200 flex items-center justify-center">
           <CircleUser className="h-6 w-6 text-slate-600" />
        </div>
      </div>
    </header>
  );
};

export default Header;