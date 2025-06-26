// bytchat-panel/src/components/modals/ToolboxModal.tsx
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Bot, ModelConfig } from '@/types';
import ModelCard, { Model } from '@/components/cards/ModelCard';
import { AVAILABLE_MODELS } from '@/lib/constants';
import { useMemo, useState } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '../ui/button';
import { cn } from '@/lib/utils'; // <-- Importar cn

interface ToolboxModalProps {
  bot: Bot | null;
  isOpen: boolean;
  onClose: () => void;
  onAddModel: (model: Model) => Promise<void>;
  onRemoveModel: (modelConfig: ModelConfig) => Promise<void>;
}

const ToolboxModal = ({ bot, isOpen, onClose, onAddModel, onRemoveModel }: ToolboxModalProps) => {
  const [updatingModelId, setUpdatingModelId] = useState<string | null>(null);

  const { modelsInBot, modelsAvailable } = useMemo(() => {
    if (!bot) return { modelsInBot: [], modelsAvailable: [] };
    
    const modelsInBotIds = new Set(bot.model_configs.map(m => m.model_id));
    
    const modelsInBot = bot.model_configs
      .map(config => {
        const modelDetails = AVAILABLE_MODELS.find(m => m.id === config.model_id);
        if (!modelDetails) return null;
        return { ...modelDetails, task_type: config.task_type || modelDetails.task_type, configId: config.id };
      })
      .filter(Boolean) as (Model & { configId: number })[];

    const modelsAvailable = AVAILABLE_MODELS.filter(m => !modelsInBotIds.has(m.id));

    return { modelsInBot, modelsAvailable };
  }, [bot]);
  
  if (!bot) return null;

  const handleAddModel = async (model: Model) => {
    setUpdatingModelId(model.id);
    await onAddModel(model);
    setUpdatingModelId(null);
  }

  const handleRemoveModel = async (model: Model & { configId: number }) => {
    setUpdatingModelId(model.id);
    const configToRemove = bot.model_configs.find(c => c.id === model.configId);
    if (configToRemove) await onRemoveModel(configToRemove);
    setUpdatingModelId(null);
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
        {/* --- CAMBIO PRINCIPAL: Añadir bg-white y shadow-lg --- */}
        <DialogContent 
            className="max-w-4xl flex flex-col p-0 gap-0 bg-white shadow-lg rounded-lg" 
            style={{ height: 'auto', minHeight: '60vh' }}
        >
            <DialogHeader className="p-6">
                <DialogTitle className="text-2xl font-bold text-slate-900">{bot.name}</DialogTitle>
            </DialogHeader>

            <div className="grid md:grid-cols-2 gap-x-8 px-6 flex-grow overflow-hidden">
                <div className="flex flex-col">
                    <h3 className="font-semibold text-slate-800 pb-4">Herramientas en tu Caja</h3>
                    <ScrollArea className="flex-grow">
                        <div className='pr-3 space-y-3'>
                        {modelsInBot.map(model => (
                            <ModelCard 
                                key={model.configId} 
                                model={model} 
                                actionType='remove'
                                onRemove={() => handleRemoveModel(model)}
                                isUpdating={updatingModelId === model.id}
                            />
                        ))}
                        {modelsInBot.length === 0 && (
                            <div className="flex items-center justify-center h-full min-h-24 rounded-lg border-2 border-dashed bg-slate-50">
                                <p className='text-sm text-slate-500 text-center'>Caja de herramientas vacía</p>
                            </div>
                        )}
                        </div>
                    </ScrollArea>
                </div>
                
                <div className="flex flex-col">
                    <h3 className="font-semibold text-slate-800 pb-4">Herramientas Disponibles</h3>
                    <ScrollArea className="flex-grow">
                        <div className='pr-3 space-y-3'>
                        {modelsAvailable.map(model => (
                            <ModelCard 
                                key={model.id} 
                                model={model} 
                                actionType='add'
                                onAdd={() => handleAddModel(model)}
                                isUpdating={updatingModelId === model.id}
                            />
                        ))}
                        </div>
                    </ScrollArea>
                </div>
            </div>

            <DialogFooter className="p-6 mt-6 border-t bg-slate-50 rounded-b-lg">
                <Button onClick={onClose}>Hecho</Button>
            </DialogFooter>
        </DialogContent>
    </Dialog>
  );
};

export default ToolboxModal;