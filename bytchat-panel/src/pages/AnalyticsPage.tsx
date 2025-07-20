// bytchat-panel/src/pages/AnalyticsPage.tsx

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SimpleBarChart, SimpleLineChart, DonutChart, MetricCard, DailyActivityBarChart } from "@/components/ui/charts";
import { useAuthStore } from "@/store/authStore";
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Bot, 
  Zap,
  Clock,
  Target,
  AlertCircle,
  Crown
} from 'lucide-react';

// Tipos para las respuestas de la API
interface UserAnalytics {
  current_plan: {
    plan_type: string;
    tokens_included: number;  // DEPRECATED
    bytokens_included: number;  // Nuevo sistema
    tokens_remaining: number;  // DEPRECATED
    bytokens_remaining: number;  // Nuevo sistema
    monthly_price: number;
  };
  tokens_remaining: number;  // DEPRECATED (viene del backend aún como tokens_remaining)
  tokens_used_this_month: number;
  tokens_overage: number;
  estimated_overage_cost: number;
  usage_by_provider: Record<string, number>;
  daily_usage: Array<{ date: string; tokens: number }>;
  top_topics: Array<{ topic: string; count: number }>;
}

interface AdminAnalytics {
  total_users: number;
  active_users_last_30_days: number;
  total_revenue_this_month_cents: number;
  users_by_plan: Record<string, number>;
  top_bots: Array<{ bot_name: string; usage_count: number }>;
}

const AnalyticsPage = () => {
  const { token, isSuperAdmin } = useAuthStore();
  const [userAnalytics, setUserAnalytics] = useState<UserAnalytics | null>(null);
  const [adminAnalytics, setAdminAnalytics] = useState<AdminAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      // Siempre obtener analíticas del usuario
      const userResponse = await fetch('/api/users/me/analytics', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (userResponse.ok) {
        const userData = await userResponse.json();
        setUserAnalytics(userData);
      }

      // Si es super admin, obtener también analíticas administrativas
      if (isSuperAdmin()) {
        const adminResponse = await fetch('/api/admin/analytics/overview', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (adminResponse.ok) {
          const adminData = await adminResponse.json();
          setAdminAnalytics(adminData);
        }
      }
    } catch (err) {
      setError('Error al cargar las analíticas');
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-3xl font-bold tracking-tight">Analíticas</h1>
        <div className="flex items-center justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2">Cargando analíticas...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-3xl font-bold tracking-tight">Analíticas</h1>
        <Card>
          <CardContent className="flex items-center justify-center py-16">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Error al cargar datos</h2>
              <p className="text-muted-foreground mb-4">{error}</p>
              <button 
                onClick={fetchAnalytics}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Intentar de nuevo
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Función para formatear números grandes
  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  // Función para formatear precio
  const formatPrice = (cents: number): string => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  // Preparar datos para gráficos del usuario
  const prepareUserCharts = () => {
    if (!userAnalytics) return null;

    // Datos de uso por proveedor (mes actual)
    const providerData = Object.entries(userAnalytics.usage_by_provider).map(([provider, tokens]) => ({
      label: provider.charAt(0).toUpperCase() + provider.slice(1),
      value: tokens,
      color: provider === 'openai' ? 'bg-green-500' : 
             provider === 'google' ? 'bg-blue-500' : 'bg-purple-500'
    }));

    // Datos de actividad diaria (últimos 7 días)
    const dailyData = userAnalytics.daily_usage.slice(-7).map(day => ({
      date: day.date,
      value: day.tokens
    }));

    // Datos del plan (donut chart)
    const planData = [
      {
        label: 'Tokens Usados',
        value: userAnalytics.tokens_used_this_month,
        color: '#ef4444'
      },
      {
        label: 'BytTokens Restantes',
        value: userAnalytics.tokens_remaining,  // Backend aún retorna como tokens_remaining
        color: '#22c55e'
      }
    ];

    return { providerData, dailyData, planData };
  };

  // Preparar datos para gráficos del admin
  const prepareAdminCharts = () => {
    if (!adminAnalytics) return null;

    // Distribución de usuarios por plan
    const planDistribution = Object.entries(adminAnalytics.users_by_plan).map(([plan, count]) => ({
      label: plan.charAt(0).toUpperCase() + plan.slice(1),
      value: count,
      color: plan === 'free' ? '#6b7280' : 
             plan === 'pro' ? '#3b82f6' : '#10b981'
    }));

    // Top bots
    const topBotsData = adminAnalytics.top_bots.slice(0, 5).map(bot => ({
      label: bot.bot_name,
      value: bot.usage_count,
      color: 'bg-indigo-500'
    }));

    return { planDistribution, topBotsData };
  };

  const userCharts = prepareUserCharts();
  const adminCharts = prepareAdminCharts();

  return (
    <div className="flex flex-col gap-6">
      {/* Header con indicador de rol */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Analíticas</h1>
        {isSuperAdmin() && (
          <div className="flex items-center gap-2 px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full">
            <Crown className="w-4 h-4" />
            <span className="text-sm font-medium">Vista Super Admin</span>
          </div>
        )}
      </div>

      {/* Dashboard del Usuario */}
      {userAnalytics && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">📊 Mi Dashboard Personal</h2>
          
          {/* Métricas principales del usuario */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="Plan Actual"
              value={userAnalytics.current_plan.plan_type.toUpperCase()}
              subtitle={formatPrice(userAnalytics.current_plan.monthly_price) + '/mes'}
              icon={<Target />}
              color="blue"
            />
            <MetricCard
              title="BytTokens Restantes"
              value={formatNumber(userAnalytics.tokens_remaining)}
              subtitle={`de ${formatNumber(userAnalytics.current_plan.tokens_included)}`}
              icon={<Zap />}
              color={userAnalytics.tokens_remaining < 10000 ? 'red' : 'green'}
            />
            <MetricCard
              title="Uso Este Mes"
              value={formatNumber(userAnalytics.tokens_used_this_month)}
              subtitle="tokens consumidos"
              icon={<TrendingUp />}
              color="yellow"
            />
            <MetricCard
              title="Costo Overage"
              value={formatPrice(userAnalytics.estimated_overage_cost)}
              subtitle={userAnalytics.tokens_overage > 0 ? `${formatNumber(userAnalytics.tokens_overage)} tokens extra` : 'Sin overage'}
              icon={<DollarSign />}
              color={userAnalytics.tokens_overage > 0 ? 'red' : 'green'}
            />
          </div>

          {/* Gráficos del usuario */}
          {userCharts && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Uso por IA */}
              {userCharts.providerData.length > 0 && (
                <SimpleBarChart
                  data={userCharts.providerData}
                  title="Uso por Proveedor de IA (Este Mes)"
                />
              )}

              {/* Distribución del plan */}
              <DonutChart
                data={userCharts.planData}
                title="Distribución de Tokens"
                centerText={formatNumber(userAnalytics.current_plan.tokens_included)}
              />

              {/* Actividad diaria */}
              {userCharts.dailyData.length > 0 && (
                <div className="lg:col-span-2">
                  <DailyActivityBarChart
                    data={userCharts.dailyData}
                    title="Actividad Diaria (Últimos 7 días)"
                  />
                </div>
              )}
            </div>
          )}

          {/* Temas más preguntados */}
          {userAnalytics.top_topics.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>🎯 Temas Más Preguntados</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  {userAnalytics.top_topics.map((topic, index) => (
                    <div key={index} className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-lg font-bold text-blue-600">{topic.count}</div>
                      <div className="text-sm text-muted-foreground capitalize">{topic.topic}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Dashboard del Super Admin */}
      {isSuperAdmin() && adminAnalytics && (
        <div className="space-y-6 border-t pt-6">
          <h2 className="text-xl font-semibold">👑 Dashboard de Super Admin</h2>
          
          {/* Métricas principales del admin */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="Total Usuarios"
              value={adminAnalytics.total_users}
              subtitle="registrados"
              icon={<Users />}
              color="blue"
            />
            <MetricCard
              title="Usuarios Activos"
              value={adminAnalytics.active_users_last_30_days}
              subtitle="últimos 30 días"
              icon={<Clock />}
              color="green"
            />
            <MetricCard
              title="Revenue Mensual"
              value={formatPrice(adminAnalytics.total_revenue_this_month_cents)}
              subtitle="este mes"
              icon={<DollarSign />}
              color="yellow"
            />
            <MetricCard
              title="Bots Totales"
              value={adminAnalytics.top_bots.reduce((sum, bot) => sum + bot.usage_count, 0)}
              subtitle="interacciones"
              icon={<Bot />}
              color="blue"
            />
          </div>

          {/* Gráficos del admin */}
          {adminCharts && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Distribución de usuarios por plan */}
              <DonutChart
                data={adminCharts.planDistribution}
                title="Usuarios por Plan"
                centerText={adminAnalytics.total_users.toString()}
              />

              {/* Top bots más usados */}
              {adminCharts.topBotsData.length > 0 && (
                <SimpleBarChart
                  data={adminCharts.topBotsData}
                  title="Bots Más Usados"
                />
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnalyticsPage;