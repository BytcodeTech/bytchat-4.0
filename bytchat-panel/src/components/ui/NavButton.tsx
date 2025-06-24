import { type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavButtonProps {
  icon: LucideIcon;
  label: string;
  isActive?: boolean;
}

const NavButton = ({ icon: Icon, label, isActive = false }: NavButtonProps) => {
  return (
    <a
      href="#"
      className={cn(
        'flex items-center space-x-3 px-4 py-2 rounded-lg transition-colors',
        isActive
          ? 'bg-sky-700 text-white'
          : 'text-slate-300 hover:bg-slate-700 hover:text-white'
      )}
    >
      <Icon className="w-5 h-5" />
      <span>{label}</span>
    </a>
  );
};

export default NavButton;