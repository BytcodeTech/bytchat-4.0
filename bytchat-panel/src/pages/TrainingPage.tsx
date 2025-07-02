import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, FileText, FileType2, Trash2 } from 'lucide-react';
import api from '@/lib/api';

interface Bot {
  id: number;
  name: string;
}

interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  status: string;
  vector_index_path?: string;
}

const TrainingPage: React.FC = () => {
  const [bots, setBots] = useState<Bot[]>([]);
  const [selectedBotId, setSelectedBotId] = useState<number | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    // Cargar bots al montar
    api.get<Bot[]>('/bots/')
      .then(res => setBots(res.data))
      .catch(() => setError('No se pudieron cargar los bots.'));
  }, []);

  useEffect(() => {
    if (selectedBotId) {
      setIsLoadingDocs(true);
      api.get<Document[]>(`/bots/${selectedBotId}/documents/`)
        .then(res => setDocuments(res.data))
        .catch(() => setError('No se pudieron cargar los documentos.'))
        .finally(() => setIsLoadingDocs(false));
    } else {
      setDocuments([]);
    }
  }, [selectedBotId]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !selectedBotId) return;
    setIsUploading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post(`/bots/${selectedBotId}/documents/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setFile(null);
      // Refrescar documentos
      const res = await api.get<Document[]>(`/bots/${selectedBotId}/documents/`);
      setDocuments(res.data);
    } catch (err) {
      setError('Error al subir el archivo.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (docId: number) => {
    if (!selectedBotId) return;
    if (!window.confirm('¿Seguro que deseas eliminar este documento?')) return;
    setDeletingId(docId);
    try {
      await api.delete(`/bots/${selectedBotId}/documents/${docId}`);
      setDocuments(prev => prev.filter(d => d.id !== docId));
    } catch {
      alert('Error al eliminar el documento.');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-10">
      <h1 className="text-2xl font-bold mb-6 text-slate-800">Entrenamiento de Bots</h1>
      <div className="mb-12">
        <label className="block mb-2 font-medium text-slate-700">Selecciona un bot</label>
        <Select value={selectedBotId?.toString() || ''} onValueChange={val => setSelectedBotId(Number(val))}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Selecciona un bot..." />
          </SelectTrigger>
          <SelectContent className="z-[9999] w-full bg-white">
            {bots.map(bot => (
              <SelectItem key={bot.id} value={bot.id.toString()}>{bot.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      {selectedBotId && (
        <>
          <div className="mb-8">
            <form onSubmit={handleUpload} className="flex items-center gap-4">
              <Input type="file" accept=".pdf,.txt" onChange={handleFileChange} />
              <Button type="submit" disabled={isUploading || !file}>
                {isUploading ? <Loader2 className="animate-spin h-5 w-5 mr-2" /> : 'Subir Archivo'}
              </Button>
              {file && <span className="text-slate-600 text-sm">{file.name}</span>}
            </form>
          </div>
          <h2 className="text-lg font-semibold mb-2">Documentos Subidos</h2>
          {isLoadingDocs ? (
            <div className="flex items-center gap-2 text-slate-500"><Loader2 className="animate-spin h-5 w-5" />Cargando documentos...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {documents.length === 0 ? (
                <div className="col-span-full text-center py-8 text-slate-500 border rounded-lg bg-slate-50">No hay documentos subidos.</div>
              ) : (
                documents.map(doc => {
                  const isPdf = doc.file_type === 'application/pdf';
                  const icon = isPdf ? <FileType2 className="h-8 w-8 text-red-500" /> : <FileText className="h-8 w-8 text-blue-500" />;
                  let statusColor = 'text-slate-500';
                  if (doc.status === 'completed') statusColor = 'text-green-600';
                  else if (doc.status === 'processing') statusColor = 'text-yellow-600';
                  else if (doc.status === 'failed') statusColor = 'text-red-600';
                  return (
                    <div key={doc.id} className="flex items-center gap-4 p-4 border rounded-lg bg-white shadow-sm">
                      <div>{icon}</div>
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-slate-800 truncate">{doc.filename}</div>
                        <div className="text-xs text-slate-500">{isPdf ? 'PDF' : 'TXT'} · {(doc.file_size / 1024).toFixed(2)} KB</div>
                        <div className={`text-xs font-medium mt-1 ${statusColor}`}>{doc.status}</div>
                        <div className="text-xs text-slate-400 break-all mt-1">{doc.vector_index_path ? doc.vector_index_path : '-'}</div>
                      </div>
                      <button
                        className="p-2 rounded hover:bg-slate-100 transition"
                        title="Eliminar documento"
                        onClick={() => handleDelete(doc.id)}
                        disabled={deletingId === doc.id}
                      >
                        {deletingId === doc.id ? (
                          <Loader2 className="h-5 w-5 animate-spin text-red-600" />
                        ) : (
                          <Trash2 className="h-5 w-5 text-slate-400 hover:text-red-600" />
                        )}
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          )}
        </>
      )}
      {error && <div className="mt-4 text-red-600">{error}</div>}
    </div>
  );
};

export default TrainingPage; 