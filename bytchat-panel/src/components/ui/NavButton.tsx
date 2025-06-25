import { type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavButtonProps {
  icon: LucideIcon;
  label: string;
  isActive?: boolean;
  onClick?: () => void; // <-- 1. Añadimos la propiedad onClick
}

const NavButton = ({ icon: Icon, label, isActive = false, onClick }: NavButtonProps) => {
  // --- 2. Cambiamos la etiqueta <a> por <button> para manejar la acción ---
  return (
    <button
      onClick={onClick}
      type="button" // Es buena práctica definir el tipo
      className={cn(
        'flex items-center space-x-3 px-4 py-2 rounded-lg transition-colors w-full text-left', // Aseguramos que ocupe todo el ancho
        isActive
          ? 'bg-sky-700 text-white'
          : 'text-slate-300 hover:bg-slate-700 hover:text-white'
      )}
    >
      <Icon className="w-5 h-5" />
      <span>{label}</span>
    </button>
  );
};

export default NavButton;