import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Icons } from '@/components/ui/icons'; // <-- Importamos los iconos

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
      setSuccess('¡Cuenta creada! Serás redirigido al login.');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="w-full lg:grid lg:min-h-screen lg:grid-cols-2">
       <div className="flex items-center justify-center py-12">
        <div className="mx-auto grid w-[350px] gap-6">
          <div className="grid gap-2 text-center">
            <h1 className="text-3xl font-bold">Crea tu Cuenta</h1>
            <p className="text-balance text-muted-foreground">
              Bienvenido. Completa el formulario para empezar.
            </p>
          </div>
          <form onSubmit={handleSubmit} className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="full-name">Nombre Completo</Label>
              <Input id="full-name" placeholder="John Doe" required value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="m@ejemplo.com" required value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Contraseña</Label>
              <Input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            {success && <p className="text-sm text-green-600">{success}</p>}
            <Button type="submit" className="w-full">
              Crear Cuenta
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
            ¿Ya tienes una cuenta?{' '}
            <Link to="/login" className="underline">
              Inicia Sesión
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

export default RegisterPage;