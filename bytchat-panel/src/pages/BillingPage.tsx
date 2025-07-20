import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore } from "@/store/authStore";
import { 
  CreditCard, 
  Download, 
  CheckCircle, 
  Star,
  Zap,
  Crown,
  Calendar,
  DollarSign,
  Users,
  Bot,
  Globe,
  ArrowRight
} from 'lucide-react';

// Tipos para los planes
type PlanType = 'FREE' | 'PRO' | 'ENTERPRISE';

interface Plan {
  id: PlanType;
  name: string;
  price: number;
  tokens: number;
  bots: string;
  widgets: boolean;
  support: string;
  features: string[];
  popular?: boolean;
  color: string;
}

// Configuración de planes con BytTokens
const PLANS: Plan[] = [
  {
    id: 'FREE',
    name: 'Free',
    price: 0,
    tokens: 2000,  // BytTokens ($2 valor real)
    bots: '1',
    widgets: false,
    support: 'Comunidad',
    color: 'gray',
    features: [
      '2,000 BytTokens/mes ($2 valor)',
      '~10,000 preguntas DeepSeek',
      '~1,300 preguntas Gemini',
      '~400 preguntas GPT-4o',
      '1 bot personalizado',
      'Soporte comunidad'
    ]
  },
  {
    id: 'PRO',
    name: 'Pro',
    price: 20,
    tokens: 13000,  // BytTokens ($13 valor real, $20 con 35% margen)
    bots: '5',
    widgets: true,
    support: 'Email',
    popular: true,
    color: 'blue',
    features: [
      '13,000 BytTokens/mes ($13 valor)',
      '~65,000 preguntas DeepSeek',
      '~8,600 preguntas Gemini',
      '~2,600 preguntas GPT-4o',
      'Hasta 5 bots',
      'Widgets ilimitados',
      'Analytics avanzado',
      'Soporte por email'
    ]
  },
  {
    id: 'ENTERPRISE',
    name: 'Enterprise',
    price: 100,
    tokens: 80000,  // BytTokens ($80 valor real, $100 con 20% margen)
    bots: 'Ilimitados',
    widgets: true,
    support: 'Priority',
    color: 'purple',
    features: [
      '80,000 BytTokens/mes ($80 valor)',
      '~400,000 preguntas DeepSeek',
      '~53,000 preguntas Gemini',
      '~16,000 preguntas GPT-4o',
      'Bots ilimitados',
      'Widgets ilimitados',
      'Analytics premium',
      'Soporte priority',
      'API completo',
      'SSO & SAML'
    ]
  }
];

// Datos mock del usuario actual con BytTokens
const MOCK_USER_DATA = {
  currentPlan: 'PRO' as PlanType,
  bytokensUsed: 3240,      // BytTokens usados
  bytokensIncluded: 13000, // BytTokens incluidos en el plan
  nextBilling: '2024-08-15',
  paymentMethod: '•••• 4532',
  billingHistory: [
    { date: '2024-07-15', description: 'Pro Plan', amount: 20.00, status: 'paid' },
    { date: '2024-06-15', description: 'Pro Plan', amount: 20.00, status: 'paid' },
    { date: '2024-05-15', description: 'Pro Plan', amount: 20.00, status: 'paid' },
    { date: '2024-04-15', description: 'Upgrade to Pro', amount: 20.00, status: 'paid' }
  ]
};

// Componente para el plan actual
const CurrentPlanSection: React.FC = () => {
  const currentPlanConfig = PLANS.find(p => p.id === MOCK_USER_DATA.currentPlan)!;
  const usagePercentage = (MOCK_USER_DATA.bytokensUsed / MOCK_USER_DATA.bytokensIncluded) * 100;
  const dollarValueUsed = (MOCK_USER_DATA.bytokensUsed / 1000).toFixed(2);
  const dollarValueTotal = (MOCK_USER_DATA.bytokensIncluded / 1000).toFixed(2);
  
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Crown className="w-5 h-5 text-blue-500" />
          Mi Plan Actual
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Plan Info */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                {currentPlanConfig.name}
              </span>
              <span className="text-gray-600 font-medium">${currentPlanConfig.price}/mes</span>
            </div>
            <p className="text-sm text-gray-500">Plan activo</p>
          </div>

          {/* Usage */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">BytTokens usados</span>
              <span className="text-sm text-gray-600">
                {MOCK_USER_DATA.bytokensUsed.toLocaleString()} / {MOCK_USER_DATA.bytokensIncluded.toLocaleString()}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                style={{ width: `${Math.min(usagePercentage, 100)}%` }}
              />
            </div>
            <p className="text-xs text-gray-500">
              {usagePercentage.toFixed(1)}% utilizado (${dollarValueUsed} de ${dollarValueTotal})
            </p>
          </div>

          {/* Next Billing */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span className="text-sm font-medium">Próximo pago</span>
            </div>
            <p className="text-sm text-gray-600">{MOCK_USER_DATA.nextBilling}</p>
            <p className="text-xs text-gray-500">${currentPlanConfig.price}.00</p>
          </div>

          {/* Payment Method */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-gray-400" />
              <span className="text-sm font-medium">Método de pago</span>
            </div>
            <p className="text-sm text-gray-600">{MOCK_USER_DATA.paymentMethod}</p>
            <button className="text-xs text-blue-600 hover:text-blue-800">Cambiar</button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Componente para cada plan
const PlanCard: React.FC<{ plan: Plan; current: boolean; onSelect: () => void }> = ({ 
  plan, 
  current, 
  onSelect 
}) => {
  const getIconForPlan = (planId: PlanType) => {
    switch (planId) {
      case 'FREE': return <Zap className="w-5 h-5" />;
      case 'PRO': return <Star className="w-5 h-5" />;
      case 'ENTERPRISE': return <Crown className="w-5 h-5" />;
    }
  };

  return (
    <Card className={`relative transition-all duration-200 hover:shadow-lg ${
      current ? 'ring-2 ring-blue-500' : ''
    } ${plan.popular ? 'ring-2 ring-orange-400' : ''}`}>
      {plan.popular && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <span className="bg-orange-500 text-white px-3 py-1 rounded-full text-xs font-medium">
            Más Popular
          </span>
        </div>
      )}
      
      <CardHeader className="text-center pb-4">
        <div className="flex items-center justify-center mb-2">
          {getIconForPlan(plan.id)}
        </div>
        <CardTitle className="text-xl">{plan.name}</CardTitle>
        <div className="space-y-1">
          <div className="flex items-baseline justify-center gap-1">
            <span className="text-3xl font-bold">${plan.price}</span>
            <span className="text-gray-500">/mes</span>
          </div>
          <p className="text-sm text-gray-600">{plan.tokens.toLocaleString()} BytTokens (${(plan.tokens/1000).toFixed(0)} valor)</p>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Features */}
        <ul className="space-y-2">
          {plan.features.map((feature, index) => (
            <li key={index} className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-600">{feature}</span>
            </li>
          ))}
        </ul>

        {/* Action Button */}
        <div className="pt-4">
          {current ? (
            <div className="w-full py-2 text-center bg-gray-100 text-gray-600 rounded-lg font-medium">
              Plan Actual
            </div>
          ) : (
            <button
              onClick={onSelect}
              className={`w-full py-2 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
                plan.id === 'ENTERPRISE' 
                  ? 'bg-purple-600 hover:bg-purple-700 text-white'
                  : plan.id === 'PRO'
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-800 hover:bg-gray-900 text-white'
              }`}
            >
              {plan.price > PLANS.find(p => p.id === MOCK_USER_DATA.currentPlan)!.price ? 'Upgrade' : 'Cambiar'}
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Componente para el historial de pagos
const PaymentHistorySection: React.FC = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-green-500" />
          Historial de Pagos
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {MOCK_USER_DATA.billingHistory.map((payment, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div>
                  <p className="font-medium text-sm">{payment.description}</p>
                  <p className="text-xs text-gray-500">{payment.date}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-medium">${payment.amount.toFixed(2)}</span>
                <button className="text-blue-600 hover:text-blue-800">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-4 pt-4 border-t">
          <button className="text-sm text-blue-600 hover:text-blue-800">
            Ver historial completo →
          </button>
        </div>
      </CardContent>
    </Card>
  );
};

// Componente principal
const BillingPage: React.FC = () => {
  const [selectedPlan, setSelectedPlan] = useState<PlanType | null>(null);
  const { user } = useAuthStore();

  const handlePlanSelect = (planId: PlanType) => {
    setSelectedPlan(planId);
    // TODO: Aquí irá la lógica de Stripe cuando la implementemos
    alert(`Seleccionaste el plan ${planId}. La integración con Stripe vendrá pronto!`);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">💳 Facturación</h1>
        <div className="text-sm text-gray-500">
          Usuario: {user?.email}
        </div>
      </div>

      {/* Plan Actual */}
      <CurrentPlanSection />

      {/* Selector de Planes */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Star className="w-5 h-5 text-orange-500" />
            Explorar Planes
          </CardTitle>
          <p className="text-gray-600">Cambia o mejora tu plan en cualquier momento</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {PLANS.map((plan) => (
              <PlanCard
                key={plan.id}
                plan={plan}
                current={plan.id === MOCK_USER_DATA.currentPlan}
                onSelect={() => handlePlanSelect(plan.id)}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Historial de Pagos */}
      <PaymentHistorySection />

      {/* Footer Info */}
      <Card>
        <CardContent className="pt-6">
          <div className="text-center space-y-2">
            <p className="text-sm text-gray-600">
              ¿Tienes preguntas sobre facturación? <a href="#" className="text-blue-600 hover:text-blue-800">Contáctanos</a>
            </p>
            <p className="text-xs text-gray-500">
              Los pagos se procesan de forma segura. Puedes cancelar tu suscripción en cualquier momento.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default BillingPage; 