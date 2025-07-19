// bytchat-panel/src/components/cards/ModelCard.tsx
import { Button } from '@/components/ui/button';
import { BrainCircuit, Loader2 } from 'lucide-react';
import { Icons } from '../ui/icons';
import { cn } from '@/lib/utils';

export type Model = {
  id: string; 
  name: string;
  provider: 'google' | 'openai' | 'deepseek' | string;
  task_type: 'simple' | 'complex' | string;
  comingSoon?: boolean;
};

type ModelCardProps = {
  model: Model;
  onAdd?: () => void;
  onRemove?: () => void;
  isUpdating?: boolean;
  actionType: 'add' | 'remove';
};

// Mapa de estilos para cada proveedor
const providerStyles = {
  google: {
    icon: Icons.google,
    textColor: 'text-blue-800',
    bgColor: 'bg-blue-50',
    borderColor: 'border-l-blue-500', // <-- CLASE ESPECÍFICA PARA EL BORDE IZQUIERDO
    actionColor: 'text-blue-600 hover:text-blue-800',
  },
  openai: {
    icon: () => <BrainCircuit className="h-5 w-5 text-green-600" />,
    textColor: 'text-green-800',
    bgColor: 'bg-green-50',
    borderColor: 'border-l-green-500',
    actionColor: 'text-green-600 hover:text-green-800',
  },
  deepseek: {
    icon: () => <BrainCircuit className="h-5 w-5 text-purple-600" />,
    textColor: 'text-purple-800',
    bgColor: 'bg-purple-50',
    borderColor: 'border-l-purple-500',
    actionColor: 'text-purple-600 hover:text-purple-800',
  },
  default: {
    icon: () => <BrainCircuit className="h-5 w-5 text-slate-600" />,
    textColor: 'text-slate-800',
    bgColor: 'bg-slate-100',
    borderColor: 'border-l-slate-500',
    actionColor: 'text-slate-600 hover:text-slate-800',
  }
};

const ModelCard = ({ model, onAdd, onRemove, isUpdating = false, actionType }: ModelCardProps) => {
  const styles = providerStyles[model.provider as keyof typeof providerStyles] || providerStyles.default;
  const IconComponent = styles.icon;

  const actionButtonText = actionType === 'add' ? 'Añadir' : 'Quitar';
  const actionHandler = actionType === 'add' ? onAdd : onRemove;
  // Usamos un color para el botón de quitar más genérico, como en la referencia
  const actionColorClass = actionType === 'add' ? styles.actionColor : 'text-slate-600 hover:text-slate-800';

  return (
    <div className={cn(
      // Estilos base: borde gris muy sutil, y borde izquierdo de 4px
      "flex items-center p-3 rounded-lg border border-slate-200 border-l-4",
      // Aplicamos el color solo al borde izquierdo
      styles.borderColor,
      // Aplicamos el color de fondo
      actionType === 'add' ? styles.bgColor : 'bg-white',
      isUpdating && 'opacity-50 pointer-events-none'
    )}>
      <div className="flex items-center gap-3 flex-grow">
        <IconComponent className="h-6 w-6" />
        <div>
          <p className={cn("font-semibold text-sm leading-tight", styles.textColor)}>{model.name}</p>
          <p className="text-xs text-slate-500 capitalize leading-tight">
            {model.provider} - Tarea {model.task_type}
          </p>
        </div>
      </div>
      <div className="w-28 text-right">
        {model.comingSoon ? (
          <span className="inline-block px-2 py-1 text-xs font-bold text-orange-600 bg-orange-100 rounded">Próximamente</span>
        ) : isUpdating ? (
          <Loader2 className="h-5 w-5 animate-spin text-slate-400 inline-block" />
        ) : (
          <Button variant="link" className={cn("p-0 h-auto font-semibold", actionColorClass)} onClick={actionHandler}>
            {actionButtonText}
          </Button>
        )}
      </div>
    </div>
  );
};

export default ModelCard;