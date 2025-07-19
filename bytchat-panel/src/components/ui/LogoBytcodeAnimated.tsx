import React from 'react';

export const LogoBytcodeAnimated: React.FC<{ className?: string; onlyA?: boolean }> = ({ className = '', onlyA = false }) => (
  <div className={`flex flex-col items-center ${className}`} style={{ aspectRatio: '1/1' }}>
    {/* Logo animado con sombra y hover */}
    <svg
      viewBox="0 0 100 100"
      width="100%"
      height="100%"
      className="block logo-svg-shadow logo-svg-hover"
      aria-label="Logo Bytcode Assist"
    >
      {/* Trazo animado de la A */}
      <path
        d="M 15 90 L 50 10 L 85 90"
        stroke="#fff"
        strokeWidth="12"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
        className="logo-a-stroke"
      />
      {/* Flecha azul animada */}
      <path
        className="logo-arrow"
        d="M 30 60 L 75 45 L 65 30"
        fill="#3B82F6"
      />
    </svg>
    {!onlyA && (
      <>
        <h1 className="text-3xl font-bold tracking-wider text-white logo-text-main">BYTCODE</h1>
        <p className="text-xl font-semibold text-blue-500 tracking-widest logo-text-sub">ASSIST</p>
      </>
    )}
    <style>{`
      .logo-svg-shadow {
        filter: drop-shadow(0 2px 12px rgba(59,130,246,0.15));
        transition: filter 0.3s cubic-bezier(0.77,0,0.18,1), transform 0.3s cubic-bezier(0.77,0,0.18,1);
      }
      .logo-svg-hover:hover {
        filter: drop-shadow(0 0 24px #3B82F6) drop-shadow(0 2px 12px rgba(59,130,246,0.15));
        transform: scale(1.06) translateY(-2px);
      }
      .logo-a-stroke {
        stroke-dasharray: 260;
        stroke-dashoffset: 260;
        animation: draw-a 1.2s cubic-bezier(0.77,0,0.18,1) forwards;
      }
      @keyframes draw-a {
        to { stroke-dashoffset: 0; }
      }
      .logo-arrow {
        opacity: 0;
        transform: scale(0.8);
        animation: arrow-fade-in 0.5s 1.1s cubic-bezier(0.77,0,0.18,1) forwards, arrow-pulse 2.5s 1.7s infinite cubic-bezier(0.77,0,0.18,1);
      }
      @keyframes arrow-fade-in {
        to { opacity: 1; transform: scale(1); }
      }
      @keyframes arrow-pulse {
        0%, 100% { filter: drop-shadow(0 0 0px #3B82F6); }
        50% { filter: drop-shadow(0 0 16px #60a5fa); }
      }
      .logo-text-main {
        opacity: 0;
        transform: translateY(16px);
        animation: text-fade-in 0.7s 1.5s cubic-bezier(0.77,0,0.18,1) forwards;
      }
      .logo-text-sub {
        opacity: 0;
        transform: translateY(16px);
        animation: text-fade-in 0.7s 1.8s cubic-bezier(0.77,0,0.18,1) forwards;
      }
      @keyframes text-fade-in {
        to { opacity: 1; transform: translateY(0); }
      }
    `}</style>
  </div>
);

export default LogoBytcodeAnimated; 