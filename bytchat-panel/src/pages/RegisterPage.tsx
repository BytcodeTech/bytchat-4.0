import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Icons } from '@/components/ui/icons';
import LogoBytcodeAnimated from '@/components/ui/LogoBytcodeAnimated';
import BubblesBackground from '@/components/ui/BubblesBackground';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    try {
      const response = await fetch('/api/users/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name: fullName, email: email, password: password }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Error al crear la cuenta.');
      }
      setSuccess('¡Cuenta creada exitosamente! Tu solicitud está pendiente de aprobación. Te notificaremos cuando sea aprobada.');
      setTimeout(() => navigate('/login'), 3000);
    } catch (err: any) {
      setError(err.message);
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
      <div className="flex items-center justify-center py-12 lg:py-0 bg-white">
        <div className="mx-auto w-full max-w-md">
          <div className="bg-white/95 border border-slate-100 shadow-lg rounded-2xl px-8 py-10 animate-fade-in-up transition-all duration-700">
            <div className="grid gap-2 text-center mb-6">
              <h1 className="text-3xl font-bold">Crea tu Cuenta</h1>
              <p className="text-balance text-muted-foreground">
                Bienvenido. Completa el formulario para empezar.
              </p>
            </div>
            <form onSubmit={handleSubmit} className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="full-name">Nombre Completo</Label>
                <Input id="full-name" placeholder="John Doe" required value={fullName} onChange={(e) => setFullName(e.target.value)}
                  className="bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-all duration-200 shadow-sm focus:shadow-md" />
              </div>
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
              {success && <p className="text-sm text-green-600 animate-fade-in">{success}</p>}
              <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all duration-200 focus:ring-2 focus:ring-blue-400 focus:outline-none">
                Crear Cuenta
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
              ¿Ya tienes una cuenta?{' '}
              <Link to="/login" className="underline">
                Inicia Sesión
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

export default RegisterPage;