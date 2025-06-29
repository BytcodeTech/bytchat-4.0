import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Icons } from '@/components/ui/icons'; // <-- Importamos los iconos
import axios from 'axios';

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
      login(response.data.access_token);
      navigate('/');
    } catch (err) {
      setError('Email o contraseña incorrectos.');
    }
  };

  return (
    <div className="w-full lg:grid lg:min-h-screen lg:grid-cols-2">
      <div className="flex items-center justify-center py-12">
        <div className="mx-auto grid w-[350px] gap-6">
          <div className="grid gap-2 text-center">
            <h1 className="text-3xl font-bold">Inicia Sesión</h1>
            <p className="text-balance text-muted-foreground">
              Ingresa tu email para acceder a tu panel.
            </p>
          </div>
          <form onSubmit={handleLogin} className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="m@ejemplo.com" required value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Contraseña</Label>
              <Input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit" className="w-full">
              Entrar
            </Button>
          </form>
          {/* --- Divisor y Botones Sociales --- */}
          <div className="relative my-2">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-muted-foreground">O continuar con</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Button variant="outline" type="button" onClick={() => alert('Funcionalidad próximamente')}>
              <Icons.github className="mr-2 h-4 w-4" />
              GitHub
            </Button>
            <Button variant="outline" type="button" onClick={() => alert('Funcionalidad próximamente')}>
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
      <div className="hidden bg-slate-800 lg:flex items-center justify-center flex-col text-white p-12">
        <div className="w-24 h-24 bg-sky-600 rounded-full flex items-center justify-center font-bold text-5xl mb-6">
          B
        </div>
        <h2 className="text-4xl font-extrabold mb-2">Bytchat Panel 4.0</h2>
        <p className="text-slate-300 text-lg text-center">
          La plataforma inteligente para gestionar tus asistentes de IA.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;