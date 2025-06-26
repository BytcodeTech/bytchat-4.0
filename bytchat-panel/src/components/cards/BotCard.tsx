// bytchat-panel/src/components/cards/BotCard.tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BrainCircuit, Settings, Trash2 } from 'lucide-react';
import { Bot } from '@/types';

interface BotCardProps {
  bot: Bot;
  onManageClick: () => void; // <-- 1. AÑADIR LA PROP
}

const BotCard = ({ bot, onManageClick }: BotCardProps) => { // <-- 2. RECIBIR LA PROP
  return (
    <Card className="flex flex-col">
      {/* ... CardHeader y CardContent se mantienen igual ... */}
      <CardHeader>
        <div className="flex items-start justify-between">
            <CardTitle className="font-bold text-slate-800">{bot.name}</CardTitle>
            <div className="flex items-center justify-center w-10 h-10 bg-slate-100 rounded-lg">
                <BrainCircuit className="w-6 h-6 text-slate-600" />
            </div>
        </div>
        <CardDescription>{bot.description}</CardDescription>
      </CardHeader>
      <CardContent className="flex-grow">
        <div className="space-y-2">
            <h4 className="font-semibold text-sm text-slate-600">Modelos Activos:</h4>
            <div className="flex flex-wrap gap-2">
                {bot.model_configs.map((model) => (
                    <span key={model.id} className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                        {model.provider}
                    </span>
                ))}
                {bot.model_configs.length === 0 && (
                    <span className="text-xs text-slate-500">Ningún modelo añadido.</span>
                )}
            </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-end gap-2">
        <Button variant="ghost" size="sm" className="text-slate-600">
            <Trash2 className="h-4 w-4" />
        </Button>
        {/* --- 3. LLAMAR A LA FUNCIÓN EN EL EVENTO onClick --- */}
        <Button variant="outline" size="sm" onClick={onManageClick}>
          <Settings className="mr-2 h-4 w-4" />
          Gestionar
        </Button>
      </CardFooter>
    </Card>
  );
};

export default BotCard;