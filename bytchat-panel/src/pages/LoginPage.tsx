import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Icons } from '@/components/ui/icons'; // <-- Importamos los iconos
import axios from 'axios';
import LogoBytcodeAnimated from '@/components/ui/LogoBytcodeAnimated';
import BubblesBackground from '@/components/ui/BubblesBackground';

const LoginPage = () => {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [email, setEmail] = useState('test@example.com');
  const [password, setPassword] = useState('string');
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    try {
      const response = await axios.post('/api/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      
      // Obtener información del usuario
      const userResponse = await axios.get('/api/users/me/', {
        headers: { 'Authorization': `Bearer ${response.data.access_token}` }
      });
      
      login(response.data.access_token, userResponse.data);
      navigate('/');
    } catch (err) {
      setError('Email o contraseña incorrectos.');
    }
  };

  return (
    <div className="w-full min-h-screen lg:grid lg:grid-cols-2 bg-white">
      {/* Header móvil con logo y burbujas */}
      <div className="block lg:hidden w-full bg-slate-800 relative" style={{ height: '100px' }}>
        <BubblesBackground />
        <div className="relative z-10 flex items-center justify-center h-full px-3">
          <LogoBytcodeAnimated onlyA className="w-10 h-10" />
          <div className="ml-3 flex flex-col justify-center">
            <span className="text-base font-bold text-white leading-tight">BYTCODE</span>
            <span className="text-xs font-semibold text-blue-400 leading-tight">ASSIST</span>
          </div>
        </div>
      </div>
      {/* Formulario */}
      <div className="flex items-center justify-center py-12 lg:py-0 bg-white min-h-screen">
        <div className="mx-auto w-full max-w-md" style={{ maxWidth: 420, minWidth: 320 }}>
          <div className="bg-white/95 border border-slate-100 shadow-lg rounded-2xl px-8 py-10 animate-fade-in-up transition-all duration-700">
            <div className="grid gap-2 text-center mb-6">
              <h1 className="text-3xl font-bold">Inicia Sesión</h1>
              <p className="text-balance text-muted-foreground">
                Ingresa tu email para acceder a tu panel.
              </p>
            </div>
            <form onSubmit={handleLogin} className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="m@ejemplo.com" required value={email} onChange={(e) => setEmail(e.target.value)}
                  className="bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-all duration-200 shadow-sm focus:shadow-md" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password">Contraseña</Label>
                <Input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                  className="bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-all duration-200 shadow-sm focus:shadow-md" />
              </div>
              {error && <p className="text-sm text-red-600 animate-fade-in">{error}</p>}
              <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all duration-200 focus:ring-2 focus:ring-blue-400 focus:outline-none">
                Entrar
              </Button>
            </form>
            {/* --- Divisor y Botones Sociales --- */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-slate-200 transition-colors duration-300 group-hover:border-blue-400" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-muted-foreground">O continuar con</span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-2">
              <Button variant="outline" type="button" className="transition-all duration-200 hover:shadow-md" onClick={() => alert('Funcionalidad próximamente')}>
                <Icons.github className="mr-2 h-4 w-4" />
                GitHub
              </Button>
              <Button variant="outline" type="button" className="transition-all duration-200 hover:shadow-md" onClick={() => alert('Funcionalidad próximamente')}>
                <Icons.google className="mr-2 h-4 w-4" />
                Google
              </Button>
            </div>
            <div className="mt-4 text-center text-sm">
              ¿No tienes una cuenta?{' '}
              <Link to="/register" className="underline">
                Regístrate
              </Link>
            </div>
          </div>
        </div>
      </div>
      {/* Panel azul lateral solo en escritorio */}
      <div className="hidden lg:flex bg-slate-800 items-center justify-center flex-col text-white p-12 relative overflow-hidden">
        <BubblesBackground />
        <div className="relative z-10 flex flex-col items-center">
          <LogoBytcodeAnimated />
          <p className="text-slate-300 text-lg text-center mt-2">
            La plataforma inteligente para gestionar tus asistentes de IA.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;

<style>{`
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-up {
  animation: fade-in-up 0.7s cubic-bezier(0.77,0,0.18,1);
}
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fade-in {
  animation: fade-in 0.4s cubic-bezier(0.77,0,0.18,1);
}
`}</style>