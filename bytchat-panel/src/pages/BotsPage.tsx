// bytchat-panel/src/pages/BotsPage.tsx
import { useEffect, useState } from 'react';
import { Bot, ModelConfig } from '@/types';
import api from '@/lib/api';
import BotCard from '@/components/cards/BotCard';
import { Button } from '@/components/ui/button';
import { Loader2, PlusCircle, ServerCrash } from 'lucide-react';
import ToolboxModal from '@/components/modals/ToolboxModal';
import { Model } from '@/components/cards/ModelCard';

const BotsPage = () => {
  const [bots, setBots] = useState<Bot[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedBot, setSelectedBot] = useState<Bot | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

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

  const handleOpenModal = (bot: Bot) => {
    setSelectedBot(bot);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedBot(null);
  };

  // --- FUNCIÓN PARA AÑADIR UN MODELO (CORREGIDA) ---
  const handleAddModel = async (model: Model) => {
    if (!selectedBot) return;

    try {
      // --- LA LÍNEA CORREGIDA ESTÁ AQUÍ ---
      // Ahora también enviamos el task_type que viene del modelo.
      const response = await api.post<ModelConfig>(`/bots/${selectedBot.id}/models/`, {
        provider: model.provider,
        model_id: model.id,
        task_type: model.task_type, // <-- ESTA LÍNEA ES LA SOLUCIÓN
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
      
    } catch (err) {
      console.error("Error al añadir el modelo:", err);
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

    } catch (err) {
      console.error("Error al eliminar el modelo:", err);
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-slate-500" />
        </div>
      );
    }
    if (error) {
      return (
        <div className="flex flex-col items-center text-center h-64 justify-center bg-red-50 text-red-700 rounded-lg">
            <ServerCrash className="h-12 w-12 mb-4" />
            <h2 className="text-xl font-semibold">Error</h2>
            <p>{error}</p>
        </div>
      );
    }
    if (bots.length === 0) {
      return (
        <div className="text-center py-16 border-2 border-dashed rounded-lg">
          <h3 className="text-lg font-semibold text-slate-700">Aún no tienes bots</h3>
          <p className="text-slate-500 mt-2 mb-4">¡Crea tu primer asistente para empezar!</p>
          <Button>
            <PlusCircle className="mr-2" />
            Crear Nuevo Bot
          </Button>
        </div>
      );
    }
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {bots.map((bot) => (
          <BotCard key={bot.id} bot={bot} onManageClick={() => handleOpenModal(bot)} />
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
            <p className="mt-1 text-slate-600">
              Gestiona tus asistentes de IA y sus modelos.
            </p>
          </div>
          <Button>
            <PlusCircle className="mr-2" />
            Crear Nuevo Bot
          </Button>
        </div>
        {renderContent()}
      </div>
      <ToolboxModal 
        bot={selectedBot}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onAddModel={handleAddModel}
        onRemoveModel={handleRemoveModel}
      />
    </>
  );
};

export default BotsPage;