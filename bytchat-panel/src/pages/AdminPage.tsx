import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import Badge from '@/components/ui/badge';
import { Loader2, Clock, Check, X, Users, Shield, UserCheck, UserX } from 'lucide-react';
import api from '@/lib/api';
import { useAuthStore } from '@/store/authStore';

interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_approved: boolean;
  role: 'user' | 'admin' | 'super_admin';
  created_at: string;
  approved_at?: string;
  approved_by?: string;
}

const AdminPage = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [pendingUsers, setPendingUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isSuperAdmin } = useAuthStore();

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const [allUsersRes, pendingUsersRes] = await Promise.all([
        api.get('/admin/users/'),
        api.get('/admin/users/pending/')
      ]);
      setUsers(allUsersRes.data);
      setPendingUsers(pendingUsersRes.data);
    } catch (err: any) {
      setError('Error al cargar usuarios: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleApprove = async (userId: number) => {
    try {
      await api.post(`/admin/users/${userId}/approve/`);
      setError(null);
      fetchUsers(); // Recargar datos
    } catch (err: any) {
      setError('Error al aprobar usuario: ' + err.message);
    }
  };

  const handleReject = async (userId: number) => {
    try {
      await api.post(`/admin/users/${userId}/reject/`);
      setError(null);
      fetchUsers(); // Recargar datos
    } catch (err: any) {
      setError('Error al rechazar usuario: ' + err.message);
    }
  };

  const handleToggleApproval = async (userId: number) => {
    try {
      await api.post(`/admin/users/${userId}/toggle-approval/`);
      setError(null);
      fetchUsers(); // Recargar datos
    } catch (err: any) {
      setError('Error al cambiar estado de aprobación: ' + err.message);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Cargando usuarios...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Panel de Administración</h1>
        <p className="text-muted-foreground">
          Gestiona la autorización de usuarios en la plataforma
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Usuarios Pendientes */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Usuarios Pendientes de Aprobación
            <Badge className="ml-2">{pendingUsers.length}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {pendingUsers.length === 0 ? (
            <p className="text-muted-foreground text-center py-4">
              No hay usuarios pendientes de aprobación
            </p>
          ) : (
            <div className="space-y-4">
              {pendingUsers.map((user) => (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div>
                    <p className="font-medium">{user.email}</p>
                    <p className="text-sm text-muted-foreground">
                      Registrado: {formatDate(user.created_at)}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleApprove(user.id)}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Check className="h-4 w-4 mr-2" />
                      Aprobar
                    </Button>
                    <Button
                      onClick={() => handleReject(user.id)}
                      variant="destructive"
                    >
                      <X className="h-4 w-4 mr-2" />
                      Rechazar
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Todos los Usuarios */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Todos los Usuarios
            <Badge className="ml-2">{users.length}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {users.map((user) => (
              <div
                key={user.id}
                className="flex items-center justify-between p-4 border rounded-lg"
              >
                <div>
                  <p className="font-medium">{user.email}</p>
                  <p className="text-sm text-muted-foreground">
                    Registrado: {formatDate(user.created_at)}
                  </p>
                  {user.approved_at && (
                    <p className="text-sm text-muted-foreground">
                      Aprobado: {formatDate(user.approved_at)} por {user.approved_by}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={user.is_approved ? "bg-green-100 text-green-800" : ""}>
                    {user.is_approved ? "Aprobado" : "Pendiente"}
                  </Badge>
                  <Badge className={user.is_active ? "" : "bg-red-100 text-red-800"}>
                    {user.is_active ? "Activo" : "Inactivo"}
                  </Badge>
                  <Badge className={
                    user.role === 'super_admin' ? "bg-purple-100 text-purple-800" :
                    user.role === 'admin' ? "bg-blue-100 text-blue-800" :
                    "bg-gray-100 text-gray-800"
                  }>
                    {user.role === 'super_admin' ? 'Super Admin' :
                     user.role === 'admin' ? 'Admin' : 'Usuario'}
                  </Badge>
                  
                  {/* Botón de toggle de aprobación - Solo para Super Admin */}
                  {isSuperAdmin() && (
                    <Button
                      onClick={() => handleToggleApproval(user.id)}
                      variant="outline"
                      size="sm"
                      className="ml-2"
                      title={user.is_approved ? "Desaprobar usuario" : "Aprobar usuario"}
                    >
                      {user.is_approved ? (
                        <UserX className="h-4 w-4 text-red-600" />
                      ) : (
                        <UserCheck className="h-4 w-4 text-green-600" />
                      )}
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminPage; 