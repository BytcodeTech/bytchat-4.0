(function() {
  // Configuración por defecto
  const config = window.bytchatConfig || {};
  const botId = config.botId || 'default';
  const color = config.color || '#14305a';
  const bg = config.bg || '#f5f5f5';
  const mensaje = config.mensaje || '¡Hola! ¿En qué puedo ayudarte?';
  const logo = config.logo || 'https://cdn.jsdelivr.net/gh/lucide-icons/lucide@latest/icons/bot.svg';
  const nombre = config.nombre || 'ChatBot';

  // Crear burbuja
  const bubble = document.createElement('div');
  bubble.id = 'bytchat-bubble';
  bubble.style.position = 'fixed';
  bubble.style.right = '32px';
  bubble.style.bottom = '32px';
  bubble.style.zIndex = '10001';
  bubble.style.width = '64px';
  bubble.style.height = '64px';
  bubble.style.borderRadius = '50%';
  bubble.style.background = color;
  bubble.style.display = 'flex';
  bubble.style.alignItems = 'center';
  bubble.style.justifyContent = 'center';
  bubble.style.cursor = 'pointer';
  bubble.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
  bubble.innerHTML = `<img src="${logo}" alt="Bot" style="width:36px;height:36px;border-radius:50%;background:#fff;padding:4px;box-shadow:0 1px 4px rgba(0,0,0,0.10);object-fit:cover;" />`;
  document.body.appendChild(bubble);

  // Crear contenedor del chat
  const box = document.createElement('div');
  box.id = 'bytchat-box';
  box.style.display = 'none';
  box.style.position = 'fixed';
  box.style.right = '32px';
  box.style.bottom = '32px';
  box.style.zIndex = '10000';
  document.body.appendChild(box);

  // Función para crear el iframe SIEMPRE con tamaño por defecto
  function showChatWidget() {
    box.innerHTML = '';
    const iframe = document.createElement('iframe');
    iframe.src = `https://bytcode.tech/static/chat-widget.html?autoOpen=1&id=${encodeURIComponent(botId)}&color=${encodeURIComponent(color)}&bg=${encodeURIComponent(bg)}&mensaje=${encodeURIComponent(mensaje)}&logo=${encodeURIComponent(logo)}&nombre=${encodeURIComponent(nombre)}`;
    iframe.allow = 'microphone';
    iframe.style.width = '350px';
    iframe.style.height = '500px';
    iframe.style.borderRadius = '16px';
    iframe.style.border = 'none';
    box.appendChild(iframe);
    box.style.width = '350px';
    box.style.height = '500px';
    box.style.display = 'block';
    bubble.style.display = 'none';
  }

  // Función para mostrar la burbuja y eliminar el iframe
  function showBubble() {
    bubble.style.display = 'flex';
    box.innerHTML = '';
    box.style.display = 'none';
  }

  // Click en la burbuja: abrir el chat
  bubble.onclick = function() {
    showChatWidget();
  };

  // Escuchar mensajes del widget
  window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'bytchat-state') {
      // Solo ajustar el tamaño si el mensaje recibido es válido (no burbuja)
      if (event.data.width > 100 && event.data.height > 100) {
        box.style.width = event.data.width + 'px';
        box.style.height = event.data.height + 'px';
        box.style.right = '32px';
        box.style.bottom = '32px';
        box.style.left = 'auto';
        box.style.top = 'auto';
      }
      // Si el estado es close o minimized, mostrar la burbuja y eliminar el iframe
      if (event.data.state === 'close' || event.data.state === 'minimized') {
        showBubble();
      }
    }
  });

  // Al cargar, mostrar solo la burbuja
  showBubble();
})(); 