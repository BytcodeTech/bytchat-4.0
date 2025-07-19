import React, { useState, useRef } from "react";
import { Palette, Image as ImageIcon, MessageSquareText, UserCircle, UploadCloud, X, Monitor, Smartphone, MessageCircle, X as CloseIcon } from 'lucide-react';

export default function ChatSnippetGenerator({ botId }) {
  const [color, setColor] = useState("#14305a");
  const [bg, setBg] = useState("#f5f5f5");
  const [mensaje, setMensaje] = useState("¡Hola! ¿En qué puedo ayudarte?");
  const [logoUrl, setLogoUrl] = useState("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
  const [nombre, setNombre] = useState("ChatBot");
  const [copied, setCopied] = useState(false);
  const [uploadedLogo, setUploadedLogo] = useState(null); // File object
  const [activeTab, setActiveTab] = useState('responsive'); // 'responsive' o 'mobile'
  const [previewState, setPreviewState] = useState('bubble'); // 'bubble' o 'chat'
  const fileInputRef = useRef();

  // Si hay logo subido, usar su URL temporal, si no, usar logoUrl
  const logo = uploadedLogo ? uploadedLogo : logoUrl;

  // Cambiar la URL base para usar el dominio principal
  const baseUrl = "https://bytcode.tech/static/chat-widget.html";
  // Usar color seguro siempre
  const safeColor = color || "#14305a";
  const src = `${baseUrl}?id=${botId}&color=${encodeURIComponent(safeColor)}&bg=${encodeURIComponent(bg)}&mensaje=${encodeURIComponent(mensaje)}&logo=${encodeURIComponent(logo)}&nombre=${encodeURIComponent(nombre)}&preview=1`;
  
  // Nuevo snippet universal para integración fácil
  const universalSnippet = `<script>
  window.bytchatConfig = {
    botId: "${botId}",
    color: "${color}",
    bg: "${bg}",
    logo: "${logo}",
    nombre: "${nombre}",
    mensaje: "${mensaje}"
  };
</script>
<script src=\"/static/bytchat-integration.js\"></script>`;

  // Código responsivo mejorado con CSS inline
  const snippet = `<div style="position: relative; width: 100%; max-width: 400px; height: 600px; margin: 0 auto;">
  <iframe 
    src="${baseUrl}?id=${botId}&color=${encodeURIComponent(color)}&bg=${encodeURIComponent(bg)}&mensaje=${encodeURIComponent(mensaje)}&logo=${encodeURIComponent(logo)}&nombre=${encodeURIComponent(nombre)}" 
    style="width: 100%; height: 100%; border: none; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);"
    title="Chat Widget"
    allow="microphone"
  ></iframe>
</div>`;

  // Código alternativo para móviles (más compacto)
  const mobileSnippet = `<div style="position: fixed; bottom: 20px; right: 20px; width: 350px; height: 500px; z-index: 1000; max-width: calc(100vw - 40px); max-height: calc(100vh - 40px);">
  <iframe 
    src="${baseUrl}?id=${botId}&color=${encodeURIComponent(color)}&bg=${encodeURIComponent(bg)}&mensaje=${encodeURIComponent(mensaje)}&logo=${encodeURIComponent(logo)}&nombre=${encodeURIComponent(nombre)}" 
    style="width: 100%; height: 100%; border: none; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);"
    title="Chat Widget"
    allow="microphone"
  ></iframe>
</div>`;

  const handleCopy = () => {
    const textToCopy = activeTab === 'responsive' ? snippet : mobileSnippet;
    navigator.clipboard.writeText(textToCopy);
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

  // Función para aclarar un color hex
  function lighten(hex, percent) {
    hex = hex.replace('#', '');
    if (hex.length === 3) {
      hex = hex.split('').map(x => x + x).join('');
    }
    let r = parseInt(hex.slice(0,2),16), g = parseInt(hex.slice(2,4),16), b = parseInt(hex.slice(4,6),16);
    r = Math.min(255, Math.floor(r + (255 - r) * percent));
    g = Math.min(255, Math.floor(g + (255 - g) * percent));
    b = Math.min(255, Math.floor(b + (255 - b) * percent));
    return `rgb(${r},${g},${b})`;
  }
  const colorSecundario = lighten(color, 0.18); // degradado sutil

  // Función para manejar el clic en la burbuja
  const handleBubbleClick = () => {
    setPreviewState('chat');
  };

  // Función para minimizar el chat
  const handleMinimizeChat = () => {
    setPreviewState('bubble');
  };

  // Estilos CSS para animaciones
  const pulseAnimation = {
    animation: 'pulse 2s infinite'
  };

  const slideInAnimation = {
    animation: 'slideInFromBottom 0.3s ease-out'
  };

  return (
    <div className="bg-gradient-to-br from-white to-blue-50 rounded-xl shadow-md p-8 max-w-4xl mx-auto flex flex-col gap-8 mt-4">
      {/* Estilos CSS inline para animaciones */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
          @keyframes slideInFromBottom {
            from {
              opacity: 0;
              transform: translateY(10px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
        `
      }} />
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="flex flex-col gap-4">
          <label className="text-xs text-slate-500 flex items-center gap-2">
            <Palette className="w-4 h-4 text-blue-400" /> Color principal
            <input type="color" value={color} onChange={e => {
              if (e.target.value) setColor(e.target.value);
            }} className="ml-2 w-8 h-8 border-none bg-transparent cursor-pointer" />
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
          <span className="text-xs text-slate-500 mb-2">Vista previa interactiva:</span>
          {/* Contenedor de vista previa interactiva */}
          <div className="rounded-xl shadow-lg overflow-hidden border border-slate-100 bg-slate-50" style={{width: 350, height: 500, position: 'relative'}}>
            {/* Estado: Chat abierto */}
            {previewState === 'chat' && (
              <div className="w-full h-full relative" style={slideInAnimation}>
                {/* Header del chat */}
                <div style={{
                  width: '100%',
                  height: 70,
                  background: `linear-gradient(90deg, ${color} 0%, ${colorSecundario} 100%)`,
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0 20px',
                  borderTopLeftRadius: 16,
                  borderTopRightRadius: 16,
                  boxShadow: '0 2px 12px rgba(0,0,0,0.10)',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  zIndex: 2
                }}>
                  <img src={logo} alt="Bot" style={{width: 44, height: 44, borderRadius: '50%', background: '#fff', border: '2.5px solid #fff', objectFit: 'cover', marginRight: 16}} />
                  <div style={{display: 'flex', flexDirection: 'column'}}>
                    <span style={{fontWeight: 700, fontSize: '1.1rem', letterSpacing: 0.01}}> {nombre || 'ChatBot'} </span>
                    <span style={{fontSize: '0.98rem', opacity: 0.85}}>Estamos en línea</span>
                  </div>
                  <button 
                    onClick={handleMinimizeChat}
                    style={{marginLeft: 'auto', fontSize: 22, opacity: 0.7, cursor: 'pointer', background: 'none', border: 'none', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', width: 32, height: 32, borderRadius: '50%', transition: 'all 0.2s'}}
                    onMouseEnter={(e) => e.target.style.opacity = '1'}
                    onMouseLeave={(e) => e.target.style.opacity = '0.7'}
                  >
                    <CloseIcon size={20} />
                  </button>
                </div>
                {/* Mensaje de bienvenida */}
                <div style={{
                  position: 'absolute',
                  top: 100,
                  left: 0,
                  width: '100%',
                  display: 'flex',
                  flexDirection: 'row',
                  alignItems: 'flex-start',
                  padding: '0 24px'
                }}>
                  <img src={logo} alt="Bot" style={{width: 36, height: 36, borderRadius: '50%', background: '#fff', border: '2px solid #e6e6e6', objectFit: 'cover', marginRight: 12}} />
                  <div style={{
                    background: '#fff',
                    color: '#1a2636',
                    borderRadius: 20,
                    boxShadow: '0 6px 24px rgba(31, 38, 135, 0.10), 0 1.5px 8px rgba(0,0,0,0.07)',
                    padding: '16px 22px',
                    fontSize: '1.08rem',
                    fontWeight: 500,
                    maxWidth: '70%',
                    marginTop: 0
                  }}>{mensaje}</div>
                </div>
                {/* Input simulado */}
                <div style={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  width: '100%',
                  background: '#fff',
                  borderBottomLeftRadius: 16,
                  borderBottomRightRadius: 16,
                  boxShadow: '0 -2px 12px rgba(0,0,0,0.04)',
                  padding: '18px 16px',
                  display: 'flex',
                  alignItems: 'center',
                  zIndex: 2
                }}>
                  <input type="text" disabled value="" placeholder="Escribe tu mensaje..." style={{flex: 1, border: 'none', padding: '12px 18px', borderRadius: 18, background: '#f7fafd', fontSize: '1.08rem', color: '#0a2240', fontWeight: 500}} />
                  <button disabled style={{background: color, color: '#fff', border: 'none', borderRadius: '50%', width: 44, height: 44, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', marginLeft: 10, opacity: 0.7}}>
                    <svg viewBox="0 0 24 24" fill="none" width="26" height="26"><path d="M3 20L21 12L3 4V10L17 12L3 14V20Z" fill="currentColor"/></svg>
                  </button>
                </div>
              </div>
            )}
            
            {/* Estado: Solo burbuja */}
            {previewState === 'bubble' && (
              <div className="w-full h-full relative" style={slideInAnimation}>
                {/* Burbuja flotante interactiva */}
                <button 
                  onClick={handleBubbleClick}
                  style={{
                    position: 'absolute',
                    bottom: 24,
                    right: 24,
                    width: 56,
                    height: 56,
                    borderRadius: '50%',
                    background: color,
                    boxShadow: '0 4px 16px rgba(0,0,0,0.15), 0 2px 8px rgba(0,0,0,0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 10,
                    border: '4px solid #fff',
                    cursor: 'pointer',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    transform: 'scale(1)',
                    outline: 'none'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'scale(1.1)';
                    e.target.style.boxShadow = '0 6px 20px rgba(0,0,0,0.2), 0 4px 12px rgba(0,0,0,0.15)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'scale(1)';
                    e.target.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15), 0 2px 8px rgba(0,0,0,0.1)';
                  }}
                  onMouseDown={(e) => {
                    e.target.style.transform = 'scale(0.95)';
                  }}
                  onMouseUp={(e) => {
                    e.target.style.transform = 'scale(1.1)';
                  }}
                >
                  <img src={logo} alt="Bot" style={{width: 32, height: 32, borderRadius: '50%', background: '#fff', padding: 4, boxShadow: '0 1px 4px rgba(0,0,0,0.10)', objectFit: 'cover'}} />
                </button>
                
                {/* Indicador de mensaje (punto rojo) */}
                <div style={{
                  position: 'absolute',
                  bottom: 70,
                  right: 20,
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  background: '#ef4444',
                  border: '2px solid #fff',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                  ...pulseAnimation
                }} />
                
                {/* Texto de ayuda */}
                <div style={{
                  position: 'absolute',
                  bottom: 100,
                  right: 24,
                  background: 'rgba(0,0,0,0.8)',
                  color: '#fff',
                  padding: '8px 12px',
                  borderRadius: 8,
                  fontSize: '0.75rem',
                  fontWeight: 500,
                  whiteSpace: 'nowrap',
                  opacity: 0,
                  transform: 'translateY(10px)',
                  transition: 'all 0.3s ease',
                  pointerEvents: 'none'
                }}
                onMouseEnter={(e) => {
                  e.target.style.opacity = '1';
                  e.target.style.transform = 'translateY(0)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.opacity = '0';
                  e.target.style.transform = 'translateY(10px)';
                }}
                >
                  Haz clic para abrir el chat
                </div>
              </div>
            )}
          </div>
          
          {/* Indicador de estado */}
          <div className="mt-3 text-xs text-slate-500 flex items-center gap-2">
            <div style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: previewState === 'chat' ? '#10b981' : '#f59e0b',
              ...(previewState === 'chat' ? pulseAnimation : {})
            }} />
            {previewState === 'chat' ? 'Chat abierto' : 'Solo burbuja'}
          </div>
          
          <button
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition text-xs font-semibold"
            onClick={() => {
              const params = new URLSearchParams({
                botId,
                color: safeColor,
                bg,
                logo,
                nombre,
                mensaje
              }).toString();
              window.open(`/static/demo-burbuja.html?${params}`, '_blank');
            }}
          >
            🚀 Ver demo real (burbuja profesional)
          </button>
        </div>
      </div>
      
      {/* Sección de código con pestañas */}
      <div className="mt-4">
        <div className="flex items-center gap-4 mb-4">
          <span className="text-sm font-medium text-slate-700">Código para incrustar:</span>
          <div className="flex bg-slate-100 rounded-lg p-1">
            <button 
              onClick={() => setActiveTab('responsive')}
              className={`flex items-center gap-2 px-3 py-1 rounded-md text-xs font-medium transition ${
                activeTab === 'responsive' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              <Monitor className="w-3 h-3" />
              Universal
            </button>
          </div>
        </div>
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-500">
              Código universal (recomendado, burbuja profesional)
            </span>
            <button 
              onClick={() => {navigator.clipboard.writeText(universalSnippet); setCopied(true); setTimeout(() => setCopied(false), 1500);}} 
              className={`px-3 py-1 rounded-md text-xs font-medium text-white transition ${
                copied ? 'bg-green-500' : 'bg-blue-500 hover:bg-blue-600'
              }`}
            >
              {copied ? '¡Copiado!' : 'Copiar'}
            </button>
          </div>
          <textarea 
            value={universalSnippet} 
            readOnly 
            rows={8} 
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-xs bg-white font-mono focus:outline-none resize-none"
          />
        </div>
        <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="text-sm font-medium text-blue-800 mb-2">💡 Consejos de uso:</h4>
          <ul className="text-xs text-blue-700 space-y-1">
            <li>• Solo copia y pega el código. El chat aparecerá como burbuja flotante profesional.</li>
            <li>• Personaliza color, logo, nombre y mensaje según tu marca.</li>
            <li>• No necesitas HTML extra, el script lo crea todo.</li>
            <li>• Si tienes dudas, contacta a soporte.</li>
          </ul>
          <div className="mt-3">
            <a href="/static/INTEGRACION_WIDGET.html" target="_blank" rel="noopener noreferrer" className="text-blue-700 underline font-medium text-xs hover:text-blue-900">
              📖 Ver documentación completa de integración
            </a>
          </div>
        </div>
      </div>
    </div>
  );
} 