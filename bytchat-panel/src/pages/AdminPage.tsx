import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import Badge from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Loader2, Clock, Check, X, Users, Shield, UserCheck, UserX, 
  DollarSign, Coins, Settings, TrendingUp, Calendar
} from 'lucide-react';
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

interface UserPlan {
  id: number;
  user_id: number;
  plan_type: 'free' | 'pro' | 'enterprise';
  tokens_included: number;  // DEPRECATED
  bytokens_included: number;  // Nuevo sistema
  tokens_remaining: number;  // DEPRECATED
  bytokens_remaining: number;  // Nuevo sistema
  tokens_overage: number;
  overage_cost: number;
  monthly_price: number;
  overage_rate: number;
  started_at: string;
  current_period_start: string;
  current_period_end?: string;
}

interface UserWithPlan extends User {
  plan?: UserPlan;
  total_bots: number;
  tokens_used_last_30_days: number;
  last_activity?: string;
}

const AdminPage = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [pendingUsers, setPendingUsers] = useState<User[]>([]);
  const [usersWithPlans, setUsersWithPlans] = useState<UserWithPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('users');
  const { isSuperAdmin } = useAuthStore();

  // Estados para modales
  const [selectedUser, setSelectedUser] = useState<UserWithPlan | null>(null);
  const [changePlanOpen, setChangePlanOpen] = useState(false);
  const [modifyTokensOpen, setModifyTokensOpen] = useState(false);

  // Estados para formularios
  const [newPlanType, setNewPlanType] = useState<'free' | 'pro' | 'enterprise'>('free');
  const [tokensToAdd, setTokensToAdd] = useState<number>(0);
  const [resetUsage, setResetUsage] = useState(false);
  const [reason, setReason] = useState('');
  const [resetOverage, setResetOverage] = useState(false);

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

  const fetchUsersWithPlans = async () => {
    try {
      setLoading(true);
      const response = await api.get('/admin/users/with-plans/');
      setUsersWithPlans(response.data);
    } catch (err: any) {
      setError('Error al cargar usuarios con planes: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'users') {
      fetchUsers();
    } else if (activeTab === 'plans') {
      fetchUsersWithPlans();
    }
  }, [activeTab]);

  const handleApprove = async (userId: number) => {
    try {
      await api.post(`/admin/users/${userId}/approve/`);
      setError(null);
      fetchUsers();
    } catch (err: any) {
      setError('Error al aprobar usuario: ' + err.message);
    }
  };

  const handleReject = async (userId: number) => {
    try {
      await api.post(`/admin/users/${userId}/reject/`);
      setError(null);
      fetchUsers();
    } catch (err: any) {
      setError('Error al rechazar usuario: ' + err.message);
    }
  };

  const handleToggleApproval = async (userId: number) => {
    try {
      await api.post(`/admin/users/${userId}/toggle-approval/`);
      setError(null);
      fetchUsers();
    } catch (err: any) {
      setError('Error al cambiar estado de aprobación: ' + err.message);
    }
  };

  const handleChangePlan = async () => {
    if (!selectedUser) return;

    try {
      const payload = {
        new_plan_type: newPlanType,
        tokens_to_add: tokensToAdd > 0 ? tokensToAdd : null,
        reset_usage: resetUsage
      };

      await api.post(`/admin/users/${selectedUser.id}/change-plan/`, payload);
      setError(null);
      setChangePlanOpen(false);
      fetchUsersWithPlans();
      
      // Reset form
      setTokensToAdd(0);
      setResetUsage(false);
    } catch (err: any) {
      setError('Error al cambiar plan: ' + err.message);
    }
  };

  const handleModifyTokens = async () => {
    if (!selectedUser) return;

    try {
      const payload = {
        tokens_to_add: tokensToAdd,
        reason: reason || 'Modificación administrativa',
        reset_overage: resetOverage
      };

      await api.post(`/admin/users/${selectedUser.id}/modify-tokens/`, payload);
      setError(null);
      setModifyTokensOpen(false);
      fetchUsersWithPlans();
      
      // Reset form
      setTokensToAdd(0);
      setReason('');
      setResetOverage(false);
    } catch (err: any) {
      setError('Error al modificar tokens: ' + err.message);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES');
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('es-ES').format(num);
  };

  const getPlanBadgeColor = (plan: string) => {
    switch (plan) {
      case 'enterprise': return 'bg-purple-100 text-purple-800';
      case 'pro': return 'bg-blue-100 text-blue-800';
      default: return 'bg-green-100 text-green-800';
    }
  };

  const getPlanName = (plan: string) => {
    switch (plan) {
      case 'enterprise': return 'Enterprise';
      case 'pro': return 'Pro';
      default: return 'Free';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Cargando...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Panel de Administración</h1>
        <p className="text-muted-foreground">
          Gestiona usuarios, planes y tokens en la plataforma
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setError(null)}
            className="mt-2"
          >
            Cerrar
          </Button>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="users" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Gestión de Usuarios
          </TabsTrigger>
          {isSuperAdmin() && (
            <TabsTrigger value="plans" className="flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Planes y Tokens
            </TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="users" className="space-y-6">
          {/* Usuarios Pendientes */}
          <Card>
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
        </TabsContent>

        {isSuperAdmin() && (
          <TabsContent value="plans" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  Gestión de Planes y Tokens
                  <Badge className="ml-2">{usersWithPlans.length}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {usersWithPlans.map((user) => (
                    <div
                      key={user.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <p className="font-medium">{user.email}</p>
                          <Badge className={getPlanBadgeColor(user.plan?.plan_type || 'free')}>
                            {getPlanName(user.plan?.plan_type || 'free')}
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-muted-foreground">
                          <div>
                            <span className="font-medium">BytTokens restantes:</span>
                            <p className="text-foreground">{formatNumber(user.plan?.bytokens_remaining || 0)}</p>
                          </div>
                          <div>
                            <span className="font-medium">BytTokens incluidos:</span>
                            <p className="text-foreground">{formatNumber(user.plan?.bytokens_included || 0)}</p>
                          </div>
                          <div>
                            <span className="font-medium">Uso (30 días):</span>
                            <p className="text-foreground">{formatNumber(user.tokens_used_last_30_days)}</p>
                          </div>
                          <div>
                            <span className="font-medium">Bots creados:</span>
                            <p className="text-foreground">{user.total_bots}</p>
                          </div>
                        </div>

                        {user.plan?.tokens_overage > 0 && (
                          <div className="mt-2 p-2 bg-orange-50 border border-orange-200 rounded text-sm">
                            <span className="text-orange-800 font-medium">
                              Overage: {formatNumber(user.plan.tokens_overage)} tokens 
                              (${(user.plan.overage_cost / 100).toFixed(2)})
                            </span>
                          </div>
                        )}
                      </div>

                      <div className="flex gap-2 ml-4">
                        <Button
                          onClick={() => {
                            setSelectedUser(user);
                            setNewPlanType(user.plan?.plan_type || 'free');
                            setChangePlanOpen(true);
                          }}
                          variant="outline"
                          size="sm"
                        >
                          <Settings className="h-4 w-4 mr-2" />
                          Cambiar Plan
                        </Button>
                        <Button
                          onClick={() => {
                            setSelectedUser(user);
                            setModifyTokensOpen(true);
                          }}
                          variant="outline"
                          size="sm"
                        >
                          <Coins className="h-4 w-4 mr-2" />
                          Modificar Tokens
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>

      {/* Modal para cambiar plan */}
      <Dialog open={changePlanOpen} onOpenChange={setChangePlanOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cambiar Plan de Usuario</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Usuario: {selectedUser?.email}</Label>
              <p className="text-sm text-muted-foreground">
                Plan actual: {getPlanName(selectedUser?.plan?.plan_type || 'free')}
              </p>
            </div>

            <div>
              <Label htmlFor="plan-select">Nuevo Plan</Label>
              <Select value={newPlanType} onValueChange={(value: 'free' | 'pro' | 'enterprise') => setNewPlanType(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="free">Free (2K BytTokens)</SelectItem>
                  <SelectItem value="pro">Pro (13K BytTokens)</SelectItem>
                  <SelectItem value="enterprise">Enterprise (80K BytTokens)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="extra-tokens">BytTokens adicionales (opcional)</Label>
              <Input
                id="extra-tokens"
                type="number"
                value={tokensToAdd}
                onChange={(e) => setTokensToAdd(Number(e.target.value))}
                placeholder="0"
              />
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="reset-usage"
                checked={resetUsage}
                onCheckedChange={(checked) => setResetUsage(checked as boolean)}
              />
              <Label htmlFor="reset-usage">Resetear uso actual</Label>
            </div>

            <div className="flex gap-2 pt-4">
              <Button onClick={handleChangePlan} className="flex-1">
                Cambiar Plan
              </Button>
              <Button onClick={() => setChangePlanOpen(false)} variant="outline">
                Cancelar
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal para modificar tokens */}
      <Dialog open={modifyTokensOpen} onOpenChange={setModifyTokensOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Modificar Tokens de Usuario</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Usuario: {selectedUser?.email}</Label>
              <p className="text-sm text-muted-foreground">
                BytTokens actuales: {formatNumber(selectedUser?.plan?.bytokens_remaining || 0)}
              </p>
            </div>

            <div>
              <Label htmlFor="tokens-modify">Tokens a agregar/quitar</Label>
              <Input
                id="tokens-modify"
                type="number"
                value={tokensToAdd}
                onChange={(e) => setTokensToAdd(Number(e.target.value))}
                placeholder="Ej: 50000 (positivo para agregar, negativo para quitar)"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Usa números positivos para agregar tokens, negativos para quitar
              </p>
            </div>

            <div>
              <Label htmlFor="reason">Motivo del cambio</Label>
              <Textarea
                id="reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Ej: Bono por cliente premium, Ajuste por error, etc."
              />
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="reset-overage"
                checked={resetOverage}
                onCheckedChange={(checked) => setResetOverage(checked as boolean)}
              />
              <Label htmlFor="reset-overage">Resetear tokens de overage</Label>
            </div>

            <div className="flex gap-2 pt-4">
              <Button onClick={handleModifyTokens} className="flex-1">
                Modificar Tokens
              </Button>
              <Button onClick={() => setModifyTokensOpen(false)} variant="outline">
                Cancelar
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminPage; 