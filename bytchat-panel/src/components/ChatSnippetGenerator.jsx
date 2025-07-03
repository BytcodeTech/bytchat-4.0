import React, { useState, useRef } from "react";
import { Palette, Image as ImageIcon, MessageSquareText, UserCircle, UploadCloud, X } from 'lucide-react';

export default function ChatSnippetGenerator({ botId }) {
  const [color, setColor] = useState("#0084ff");
  const [bg, setBg] = useState("#f5f5f5");
  const [mensaje, setMensaje] = useState("¡Hola! ¿En qué puedo ayudarte?");
  const [logoUrl, setLogoUrl] = useState("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
  const [nombre, setNombre] = useState("ChatBot");
  const [copied, setCopied] = useState(false);
  const [uploadedLogo, setUploadedLogo] = useState(null); // File object
  const fileInputRef = useRef();

  // Si hay logo subido, usar su URL temporal, si no, usar logoUrl
  const logo = uploadedLogo ? uploadedLogo : logoUrl;

  const baseUrl = "http://161.132.45.210/static/chat-widget.html";
  const src = `${baseUrl}?id=${botId}&color=${encodeURIComponent(color)}&bg=${encodeURIComponent(bg)}&mensaje=${encodeURIComponent(mensaje)}&logo=${encodeURIComponent(logo)}&nombre=${encodeURIComponent(nombre)}&preview=1`;
  const snippet = `<iframe src=\"${baseUrl}?id=${botId}&color=${encodeURIComponent(color)}&bg=${encodeURIComponent(bg)}&mensaje=${encodeURIComponent(mensaje)}&logo=${encodeURIComponent(logo)}&nombre=${encodeURIComponent(nombre)}\" width=\"350\" height=\"500\" frameborder=\"0\"></iframe>`;

  const handleCopy = () => {
    navigator.clipboard.writeText(snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleLogoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setUploadedLogo(url);
    }
  };

  const handleRemoveLogo = () => {
    setUploadedLogo(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="bg-gradient-to-br from-white to-blue-50 rounded-xl shadow-md p-8 max-w-2xl mx-auto flex flex-col gap-8 mt-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="flex flex-col gap-4">
          <label className="text-xs text-slate-500 flex items-center gap-2">
            <Palette className="w-4 h-4 text-blue-400" /> Color principal
            <input type="color" value={color} onChange={e => setColor(e.target.value)} className="ml-2 w-8 h-8 border-none bg-transparent cursor-pointer" />
          </label>
          <label className="text-xs text-slate-500 flex items-center gap-2">
            <Palette className="w-4 h-4 text-blue-200" /> Color de fondo
            <input type="color" value={bg} onChange={e => setBg(e.target.value)} className="ml-2 w-8 h-8 border-none bg-transparent cursor-pointer" />
          </label>
          <label className="text-xs text-slate-500 flex items-center gap-2">
            <MessageSquareText className="w-4 h-4 text-blue-400" /> Mensaje de bienvenida
            <input value={mensaje} onChange={e => setMensaje(e.target.value)} className="ml-2 flex-1 rounded-lg border border-slate-200 px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200" />
          </label>
          <div className="flex flex-col gap-2">
            <label className="text-xs text-slate-500 flex items-center gap-2">
              <ImageIcon className="w-4 h-4 text-blue-400" /> Logo (URL)
              <input value={logoUrl} onChange={e => setLogoUrl(e.target.value)} className="ml-2 flex-1 rounded-lg border border-slate-200 px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200" disabled={!!uploadedLogo} />
            </label>
            <div className="flex items-center gap-2">
              <label className="text-xs text-slate-500 flex items-center gap-2 cursor-pointer">
                <UploadCloud className="w-4 h-4 text-blue-400" />
                <span>Subir imagen</span>
                <input type="file" accept="image/*" ref={fileInputRef} onChange={handleLogoUpload} className="hidden" disabled={!!uploadedLogo} />
              </label>
              {uploadedLogo && (
                <button type="button" onClick={handleRemoveLogo} className="ml-2 px-2 py-1 rounded bg-red-100 text-red-600 flex items-center gap-1 text-xs"><X className="w-3 h-3" />Quitar imagen</button>
              )}
            </div>
            {uploadedLogo && (
              <img src={uploadedLogo} alt="Logo preview" className="mt-2 w-12 h-12 rounded-full border border-slate-200 object-cover" />
            )}
          </div>
          <label className="text-xs text-slate-500 flex items-center gap-2">
            <UserCircle className="w-4 h-4 text-blue-400" /> Nombre del bot
            <input value={nombre} onChange={e => setNombre(e.target.value)} className="ml-2 flex-1 rounded-lg border border-slate-200 px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200" />
          </label>
        </div>
        <div className="flex flex-col items-center">
          <span className="text-xs text-slate-500 mb-2">Vista previa:</span>
          <div className="rounded-xl shadow-lg overflow-hidden border border-slate-100 bg-slate-50" style={{width: 350, minHeight: 500}}>
            <iframe src={src} width="350" height="500" frameBorder="0" title="Vista previa del chat" style={{display: 'block'}}></iframe>
          </div>
        </div>
      </div>
      <div className="mt-4">
        <span className="text-xs text-slate-500">Código para incrustar:</span>
        <div className="flex items-center gap-2 mt-2">
          <textarea value={snippet} readOnly rows={2} className="w-full rounded-lg border border-slate-200 px-2 py-1 text-sm bg-slate-50 focus:outline-none" />
          <button onClick={handleCopy} className={`px-4 py-2 rounded-lg text-white transition ${copied ? 'bg-green-500' : 'bg-blue-500 hover:bg-blue-600'}`}>{copied ? '¡Copiado!' : 'Copiar código'}</button>
        </div>
      </div>
    </div>
  );
} 