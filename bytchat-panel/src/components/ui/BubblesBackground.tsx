import React, { useRef, useEffect } from 'react';

const BUBBLE_COLORS = [
  'rgba(59,130,246,0.18)', // azul principal translúcido
  'rgba(59,130,246,0.10)',
  'rgba(59,130,246,0.25)',
  'rgba(255,255,255,0.08)', // blanco translúcido
];

function randomBetween(a: number, b: number) {
  return a + Math.random() * (b - a);
}

const BubblesBackground: React.FC<{ className?: string }> = ({ className = '' }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const bubbles = useRef<any[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    let width = canvas.width = canvas.offsetWidth;
    let height = canvas.height = canvas.offsetHeight;

    // Crear burbujas
    const numBubbles = Math.floor((width * height) / 4000);
    bubbles.current = Array.from({ length: numBubbles }, () => ({
      x: randomBetween(0, width),
      y: randomBetween(0, height),
      r: randomBetween(16, 48),
      speed: randomBetween(0.2, 0.7),
      dx: randomBetween(-0.2, 0.2),
      color: BUBBLE_COLORS[Math.floor(Math.random() * BUBBLE_COLORS.length)],
      opacity: randomBetween(0.15, 0.5),
    }));

    function animate() {
      if (!canvasRef.current) return;
      const ctx = canvasRef.current.getContext('2d');
      if (!ctx) return;
      ctx.clearRect(0, 0, width, height);
      for (const b of bubbles.current) {
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.r, 0, 2 * Math.PI);
        ctx.fillStyle = b.color;
        ctx.globalAlpha = b.opacity;
        ctx.fill();
        ctx.globalAlpha = 1;
        b.y -= b.speed;
        b.x += b.dx;
        // Si sale por arriba, reaparece abajo
        if (b.y + b.r < 0) {
          b.y = height + b.r;
          b.x = randomBetween(0, width);
        }
        // Rebote horizontal
        if (b.x - b.r < 0 || b.x + b.r > width) {
          b.dx *= -1;
        }
      }
      animationRef.current = requestAnimationFrame(animate);
    }
    animate();

    // Redimensionar
    function handleResize() {
      const canvas = canvasRef.current;
      if (!canvas) return;
      width = canvas.width = canvas.offsetWidth;
      height = canvas.height = canvas.offsetHeight;
    }
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationRef.current!);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 w-full h-full pointer-events-none z-0 ${className}`}
      style={{ display: 'block', background: 'transparent' }}
      aria-hidden="true"
    />
  );
};

export default BubblesBackground; 