import React, { useEffect, useState } from 'react';
import ChatSnippetGenerator from '@/components/ChatSnippetGenerator';
import api from '@/lib/api';
import { BotMessageSquare, FileStack, CodeXml } from 'lucide-react';

interface Bot {
  id: number;
  name: string;
  description?: string;
}

const EmbedChatPage: React.FC = () => {
  const [bots, setBots] = useState<Bot[]>([]);
  const [selectedBotId, setSelectedBotId] = useState<number | null>(null);
  const [botDocCounts, setBotDocCounts] = useState<Record<number, number>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<Bot[]>('/bots/')
      .then(async res => {
        setBots(res.data);
        const counts: Record<number, number> = {};
        await Promise.all(res.data.map(async (bot) => {
          try {
            const docs = await api.get(`/bots/${bot.id}/documents/`);
            counts[bot.id] = docs.data.length;
          } catch {
            counts[bot.id] = 0;
          }
        }));
        setBotDocCounts(counts);
      })
      .catch(() => setError('No se pudieron cargar los bots.'));
  }, []);

  return (
    <div className="max-w-5xl mx-auto py-10">
      <h1 className="text-2xl font-bold mb-6 text-slate-800 text-left">Incrustar Chat en tu Web</h1>
      <div className="mb-12">
        <label className="block mb-4 font-medium text-slate-700 text-lg text-left">Selecciona un bot</label>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 justify-start">
          {bots.map(bot => {
            const docCount = botDocCounts[bot.id] || 0;
            return (
              <div
                key={bot.id}
                onClick={() => setSelectedBotId(bot.id)}
                className={`cursor-pointer rounded-xl p-6 shadow-md transition-all duration-200 border-2 flex flex-col gap-3 bg-gradient-to-br from-blue-50 to-white hover:shadow-xl hover:-translate-y-1 ${selectedBotId === bot.id ? 'border-purple-500 ring-2 ring-purple-300' : 'border-slate-200'}`}
                style={{ minHeight: 110, maxWidth: 340 }}
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-full">
                    <CodeXml className="w-7 h-7 text-purple-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-lg text-slate-800 truncate">{bot.name}</div>
                    <div className="text-sm text-slate-500 truncate">{bot.description || 'Sin descripción'}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-2 text-sm text-slate-600">
                  <FileStack className="w-5 h-5 text-purple-400" />
                  <span>{docCount} documento{docCount !== 1 ? 's' : ''} subido{docCount !== 1 ? 's' : ''}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      {selectedBotId && (
        <div className="mt-12">
          <ChatSnippetGenerator botId={selectedBotId.toString()} />
        </div>
      )}
      {error && <div className="mt-4 text-red-600">{error}</div>}
    </div>
  );
};

export default EmbedChatPage; 