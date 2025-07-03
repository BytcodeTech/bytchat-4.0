import React, { useState } from "react";

export default function ChatSnippetGenerator({ botId }) {
  const [color, setColor] = useState("#0084ff");
  const [bg, setBg] = useState("#f5f5f5");
  const [mensaje, setMensaje] = useState("¡Hola! ¿En qué puedo ayudarte?");
  const [logo, setLogo] = useState("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
  const [nombre, setNombre] = useState("ChatBot");

  const baseUrl = "http://161.132.45.210/static/chat-widget.html";
  const src = `${baseUrl}?id=${botId}&color=${encodeURIComponent(color)}&bg=${encodeURIComponent(bg)}&mensaje=${encodeURIComponent(mensaje)}&logo=${encodeURIComponent(logo)}&nombre=${encodeURIComponent(nombre)}`;
  const snippet = `<iframe src=\"${src}\" width=\"350\" height=\"500\" frameborder=\"0\"></iframe>`;

  return (
    <div style={{maxWidth: 600, margin: "0 auto"}}>
      <label>
        Color principal:{" "}
        <input type="color" value={color} onChange={e => setColor(e.target.value)} />
      </label>
      <br />
      <label>
        Color de fondo:{" "}
        <input type="color" value={bg} onChange={e => setBg(e.target.value)} />
      </label>
      <br />
      <label>
        Mensaje de bienvenida:{" "}
        <input value={mensaje} onChange={e => setMensaje(e.target.value)} style={{width: 300}} />
      </label>
      <br />
      <label>
        Logo:{" "}
        <input value={logo} onChange={e => setLogo(e.target.value)} style={{width: 300}} />
      </label>
      <br />
      <label>
        Nombre del bot:{" "}
        <input value={nombre} onChange={e => setNombre(e.target.value)} style={{width: 200}} />
      </label>
      <br /><br />
      <h3>Vista previa:</h3>
      <iframe src={src} width="350" height="500" frameBorder="0" title="Vista previa del chat"></iframe>
      <h3>Código para incrustar:</h3>
      <textarea value={snippet} readOnly rows={3} style={{width: '100%'}} />
      <br />
      <button onClick={() => navigator.clipboard.writeText(snippet)}>Copiar código</button>
    </div>
  );
} 