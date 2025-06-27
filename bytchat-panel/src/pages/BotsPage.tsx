// bytchat-panel/src/pages/BotsPage.tsx
import { useEffect, useState } from 'react';
import { Bot, ModelConfig } from '@/types';
import api from '@/lib/api';
import BotCard from '@/components/cards/BotCard';
import { Button } from '@/components/ui/button';
import { Loader2, PlusCircle, ServerCrash } from 'lucide-react';
import ToolboxModal from '@/components/modals/ToolboxModal';
import { Model } from '@/components/cards/ModelCard';
import CreateBotModal, { BotCreateData } from '@/components/modals/CreateBotModal';
import { toast } from 'sonner';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const BotsPage = () => {
  const [bots, setBots] = useState<Bot[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedBot, setSelectedBot] = useState<Bot | null>(null);
  const [isToolboxModalOpen, setIsToolboxModalOpen] = useState(false);
  
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [botToDelete, setBotToDelete] = useState<Bot | null>(null);

  useEffect(() => {
    const fetchBots = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await api.get<Bot[]>('/bots/');
        setBots(response.data);
      } catch (err) {
        setError('No se pudieron cargar los bots. Inténtalo de nuevo más tarde.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchBots();
  }, []);

  const handleOpenToolboxModal = (bot: Bot) => {
    setSelectedBot(bot);
    setIsToolboxModalOpen(true);
  };

  const handleCloseToolboxModal = () => {
    setIsToolboxModalOpen(false);
    setSelectedBot(null);
  };

  const handleAddModel = async (model: Model) => {
    if (!selectedBot) return;
    try {
      const response = await api.post<ModelConfig>(`/bots/${selectedBot.id}/models/`, {
        provider: model.provider,
        model_id: model.id,
        task_type: model.task_type,
      });
      const newModelConfig = response.data;
      const updateBots = (prevBots: Bot[]) => 
        prevBots.map(b => 
          b.id === selectedBot.id 
            ? { ...b, model_configs: [...b.model_configs, newModelConfig] }
            : b
        );
      setBots(updateBots);
      setSelectedBot(prev => prev ? updateBots([prev])[0] : null);
      toast.success(`Modelo "${model.name}" añadido.`);
    } catch (err) {
      toast.error("No se pudo añadir el modelo.");
    }
  };
  
  const handleRemoveModel = async (modelConfig: ModelConfig) => {
    if (!selectedBot) return;
    try {
      await api.delete(`/bots/${selectedBot.id}/models/${modelConfig.id}`);
      const updateBots = (prevBots: Bot[]) =>
        prevBots.map(b => 
          b.id === selectedBot.id
            ? { ...b, model_configs: b.model_configs.filter(mc => mc.id !== modelConfig.id) }
            : b
        );
      setBots(updateBots);
      setSelectedBot(prev => prev ? updateBots([prev])[0] : null);
      toast.info(`Modelo "${modelConfig.model_id}" eliminado.`);
    } catch (err) {
      toast.error("No se pudo eliminar el modelo.");
    }
  };

  const handleCreateBot = async (data: BotCreateData) => {
    setIsSubmitting(true);
    try {
      const response = await api.post<Bot>('/bots/', data);
      const newBot = response.data;
      setBots(prev => [newBot, ...prev]);
      setIsCreateModalOpen(false);
      toast.success(`Bot "${newBot.name}" creado con éxito.`);
    } catch (err) {
      toast.error("No se pudo crear el bot.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteBot = async () => {
    if (!botToDelete) return;
    try {
      await api.delete(`/bots/${botToDelete.id}`);
      setBots(prev => prev.filter(b => b.id !== botToDelete.id));
      toast.success(`Bot "${botToDelete.name}" eliminado.`);
    } catch (err) {
      toast.error("No se pudo eliminar el bot.");
    } finally {
      setBotToDelete(null);
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return <div className="flex justify-center items-center h-64"><Loader2 className="h-8 w-8 animate-spin text-slate-500" /></div>;
    }
    if (error) {
      return <div className="flex flex-col items-center text-center h-64 justify-center bg-red-50 text-red-700 rounded-lg"><ServerCrash className="h-12 w-12 mb-4" /><h2 className="text-xl font-semibold">Error</h2><p>{error}</p></div>;
    }
    if (bots.length === 0) {
      return (
        <div className="text-center py-16 border-2 border-dashed rounded-lg">
          <h3 className="text-lg font-semibold text-slate-700">Aún no tienes bots</h3>
          <p className="text-slate-500 mt-2 mb-4">¡Crea tu primer asistente para empezar!</p>
          <Button onClick={() => setIsCreateModalOpen(true)}><PlusCircle className="mr-2" />Crear Nuevo Bot</Button>
        </div>
      );
    }
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {bots.map((bot) => (
          <BotCard key={bot.id} bot={bot} onManageClick={() => handleOpenToolboxModal(bot)} onDeleteClick={() => setBotToDelete(bot)} />
        ))}
      </div>
    );
  };

  return (
    <>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-800">Mis Bots</h1>
            <p className="mt-1 text-slate-600">Gestiona tus asistentes de IA y sus modelos.</p>
          </div>
          <Button onClick={() => setIsCreateModalOpen(true)}><PlusCircle className="mr-2" />Crear Nuevo Bot</Button>
        </div>
        {renderContent()}
      </div>
      
      <ToolboxModal bot={selectedBot} isOpen={isToolboxModalOpen} onClose={handleCloseToolboxModal} onAddModel={handleAddModel} onRemoveModel={handleRemoveModel} />
      <CreateBotModal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} onSubmit={handleCreateBot} isSubmitting={isSubmitting} />
      
      <AlertDialog open={!!botToDelete} onOpenChange={() => setBotToDelete(null)}>
        {/* --- DIÁLOGO DE ALERTA CON ESTILOS MEJORADOS --- */}
        <AlertDialogContent className="bg-white border rounded-lg shadow-lg p-6">
          <AlertDialogHeader className="pb-4">
            <AlertDialogTitle className="text-lg font-semibold text-slate-800">¿Estás absolutamente seguro?</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-600">
              Esta acción no se puede deshacer. Esto eliminará permanentemente el bot
              <span className="font-semibold text-slate-900"> {botToDelete?.name} </span> 
              y todos sus datos.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="pt-4 flex justify-end gap-3">
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteBot}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              Sí, eliminar bot
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

export default BotsPage;