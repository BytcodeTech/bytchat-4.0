import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/store/authStore";
import { useState } from "react";
import { useNavigate } from "react-router-dom";


const LoginPage = () => {
    const [email, setEmail] = useState('test@example.com');
    const [password, setPassword] = useState('string');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const login = useAuthStore((state) => state.login);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // URL de tu API de backend
        const API_URL = 'http://161.132.45.210:8001/token';

        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData.toString(),
            });

            if (!response.ok) {
                throw new Error('Email o contraseña incorrectos.');
            }

            const data = await response.json();
            
            // Guardar el token en el store y redirigir
            login(data.access_token);
            navigate('/');

        } catch (err) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError('Ocurrió un error inesperado.');
            }
        }
    };


    return (
        <div className="flex items-center justify-center min-h-screen bg-slate-100">
            <Card className="w-full max-w-sm">
                <CardHeader>
                    <CardTitle className="text-2xl">Login</CardTitle>
                    <CardDescription>
                        Ingresa tu email para acceder a tu panel de control.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleLogin}>
                        <div className="grid gap-4">
                            <div className="grid gap-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="m@example.com"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="password">Contraseña</Label>
                                <Input 
                                    id="password" 
                                    type="password" 
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                            {error && <p className="text-red-500 text-sm">{error}</p>}
                            <Button type="submit" className="w-full">
                                Iniciar Sesión
                            </Button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
};

export default LoginPage;