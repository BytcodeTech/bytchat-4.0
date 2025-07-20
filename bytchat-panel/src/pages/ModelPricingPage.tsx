import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { DollarSign, Cpu, RefreshCw, AlertTriangle, Save, Edit3 } from 'lucide-react';

// API importada correctamente (sin authStore)
import api from '../lib/api';

// Tipos TypeScript
interface ModelPricing {
  id: number;
  provider: string;
  model_id: string;
  display_name: string;
  input_cost_per_1k: number;
  output_cost_per_1k: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
  updated_by?: string;
}

interface PendingChange {
  input_cost_per_1k?: number;
  output_cost_per_1k?: number;
  is_active?: boolean;
}

const ModelPricingPage: React.FC = () => {
  const [modelPricing, setModelPricing] = useState<ModelPricing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingFallback, setUsingFallback] = useState(false);
  const [saving, setSaving] = useState(false);
  const [pendingChanges, setPendingChanges] = useState<{[key: number]: PendingChange}>({});

  // Datos estáticos como fallback (ajustados a los modelos que realmente usas)
  const fallbackData: ModelPricing[] = [
    // OpenAI - Solo los que usas
    {
      id: 1,
      provider: 'openai',
      display_name: 'GPT-4o',
      model_id: 'gpt-4o',
      input_cost_per_1k: 0.005,
      output_cost_per_1k: 0.015,
      is_active: true, // ✅ ACTIVO - Lo usas
      updated_by: 'fallback_data'
    },
    {
      id: 2,
      provider: 'openai',
      display_name: 'GPT-3.5 Turbo',
      model_id: 'gpt-3.5-turbo',
      input_cost_per_1k: 0.001,
      output_cost_per_1k: 0.002,
      is_active: true, // ✅ ACTIVO - Lo usas
      updated_by: 'fallback_data'
    },
    {
      id: 3,
      provider: 'openai',
      display_name: 'GPT-4o Mini',
      model_id: 'gpt-4o-mini',
      input_cost_per_1k: 0.00015,
      output_cost_per_1k: 0.0006,
      is_active: false, // ❌ INACTIVO - No lo usas
      updated_by: 'fallback_data'
    },
    
    // Google - Solo los que usas
    {
      id: 4,
      provider: 'google',
      display_name: 'Gemini 1.5 Pro',
      model_id: 'gemini-1.5-pro',
      input_cost_per_1k: 0.0035,
      output_cost_per_1k: 0.0105,
      is_active: true, // ✅ ACTIVO - Lo usas (Tarea Complex)
      updated_by: 'fallback_data'
    },
    {
      id: 5,
      provider: 'google',
      display_name: 'Gemini 1.5 Flash',
      model_id: 'gemini-1.5-flash',
      input_cost_per_1k: 0.000075,
      output_cost_per_1k: 0.0003,
      is_active: true, // ✅ ACTIVO - Lo usas (Tarea Simple)
      updated_by: 'fallback_data'
    },
    {
      id: 6,
      provider: 'google',
      display_name: 'Gemini Pro',
      model_id: 'gemini-pro',
      input_cost_per_1k: 0.0015,
      output_cost_per_1k: 0.0015,
      is_active: false, // ❌ INACTIVO - No lo usas (versión antigua)
      updated_by: 'fallback_data'
    },
    
    // DeepSeek - Solo los que usas
    {
      id: 7,
      provider: 'deepseek',
      display_name: 'DeepSeek Chat',
      model_id: 'deepseek-chat',
      input_cost_per_1k: 0.00014,
      output_cost_per_1k: 0.00028,
      is_active: true, // ✅ ACTIVO - Lo usas (Tarea Simple)
      updated_by: 'fallback_data'
    },
    {
      id: 8,
      provider: 'deepseek',
      display_name: 'DeepSeek Coder',
      model_id: 'deepseek-coder',
      input_cost_per_1k: 0.00014,
      output_cost_per_1k: 0.00028,
      is_active: true, // ✅ ACTIVO - Lo usas (Tarea Complex)
      updated_by: 'fallback_data'
    },
    {
      id: 9,
      provider: 'deepseek',
      display_name: 'DeepSeek V2',
      model_id: 'deepseek-v2',
      input_cost_per_1k: 0.0002,
      output_cost_per_1k: 0.0002,
      is_active: false, // ❌ INACTIVO - No lo usas (versión antigua)
      updated_by: 'fallback_data'
    },
    {
      id: 10,
      provider: 'deepseek',
      display_name: 'DeepSeek Reasoner',
      model_id: 'deepseek-reasoner',
      input_cost_per_1k: 0.002,
      output_cost_per_1k: 0.002,
      is_active: false, // ❌ INACTIVO - No lo usas
      updated_by: 'fallback_data'
    }
  ];

  // Función para obtener token automáticamente si no existe
  const ensureAuthentication = async (): Promise<boolean> => {
    try {
      // Importación dinámica para evitar problemas
      const { useAuthStore } = await import('@/store/authStore');
      const authState = useAuthStore.getState();
      
      // Si ya tenemos token, verificar si es válido
      if (authState.token) {
        try {
          await api.get('/users/me/');
          console.log('✅ Token existente válido');
          return true;
        } catch (err) {
          console.log('🔑 Token existente inválido, obteniendo nuevo...');
          authState.logout(); // Limpiar token inválido
        }
      }
      
      // Intentar obtener token con credenciales de prueba
      console.log('🔑 Obteniendo token de autenticación...');
      const formData = new URLSearchParams();
      formData.append('username', 'test@example.com');
      formData.append('password', 'string');
      
      const tokenResponse = await api.post('/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      
      // Obtener información del usuario
      const userResponse = await api.get('/users/me/', {
        headers: { 'Authorization': `Bearer ${tokenResponse.data.access_token}` }
      });
      
      // Guardar en el store
      authState.login(tokenResponse.data.access_token, userResponse.data);
      console.log('✅ Autenticación automática exitosa');
      return true;
      
    } catch (error) {
      console.error('❌ Error en autenticación automática:', error);
      return false;
    }
  };

  // Función para cargar datos con fallback automático
  const fetchModelPricing = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔄 Intentando cargar datos desde API...');
      
      // Primero asegurar autenticación
      const isAuthenticated = await ensureAuthentication();
      if (!isAuthenticated) {
        throw new Error('No se pudo autenticar automáticamente');
      }
      
      // Timeout de 10 segundos para la API real
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Timeout: API no responde')), 10000)
      );
      
      const apiPromise = api.get('/admin/model-pricing/');
      
      const response = await Promise.race([apiPromise, timeoutPromise]) as any;
      
      console.log('✅ Datos cargados desde API:', response.data);
      setModelPricing(response.data);
      setUsingFallback(false);
      
    } catch (err: any) {
      console.error('❌ Error loading from API:', err.message);
      console.log('🔄 Usando datos de fallback...');
      
      let errorMessage = `API no disponible: ${err.message}`;
      if (err.message.includes('autenticar')) {
        errorMessage = 'Error de autenticación. Usando datos de demostración.';
      } else if (err.response?.status === 401) {
        errorMessage = 'Token inválido. Usando datos de demostración.';
      } else if (err.response?.status === 403) {
        errorMessage = 'Sin permisos de administrador. Usando datos de demostración.';
      }
      
      setError(errorMessage);
      setModelPricing(fallbackData);
      setUsingFallback(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModelPricing();
  }, []);

  const handleRefresh = () => {
    setPendingChanges({}); // Limpiar cambios pendientes al recargar
    fetchModelPricing();
  };

  // Función para manejar cambios en los inputs
  const handlePriceChange = (modelId: number, field: keyof PendingChange, value: string) => {
    const numericValue = parseFloat(value) || 0;
    
    setPendingChanges(prev => ({
      ...prev,
      [modelId]: {
        ...prev[modelId],
        [field]: numericValue
      }
    }));
  };

  // Función para obtener el valor actual (con cambios o valor original)
  const getCurrentValue = (model: ModelPricing, field: keyof ModelPricing): number => {
    const pendingChange = pendingChanges[model.id];
    if (pendingChange && field in pendingChange) {
      return pendingChange[field as keyof PendingChange] as number;
    }
    return model[field] as number;
  };

  // Función para guardar cambios
  const saveChanges = async () => {
    if (Object.keys(pendingChanges).length === 0) {
      return;
    }

    try {
      setSaving(true);
      setError(null);
      console.log('💾 Guardando cambios...', pendingChanges);

      // Si estamos usando fallback, simular guardado
      if (usingFallback) {
        // Simular delay de API
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Actualizar datos locales
        setModelPricing(prev => prev.map(model => {
          const changes = pendingChanges[model.id];
          if (changes) {
            return {
              ...model,
              ...changes,
              updated_by: 'local_edit'
            };
          }
          return model;
        }));
        
        setPendingChanges({});
        console.log('✅ Cambios guardados localmente');
        return;
      }

      // Guardar en backend real
      const updates = Object.entries(pendingChanges).map(([id, changes]) => ({
        id: parseInt(id),
        ...changes
      }));

      await api.post('/admin/model-pricing/bulk-update/', {
        pricing_updates: updates,
        updated_by: 'admin_edit'
      });

      // Recargar datos del backend
      await fetchModelPricing();
      setPendingChanges({});
      
      console.log('✅ Cambios guardados en backend');
      
    } catch (err: any) {
      console.error('❌ Error guardando cambios:', err);
      setError(`Error al guardar: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const calculateBytokens = (inputCost: number, outputCost: number) => {
    // Consulta típica más realista: 500 input + 300 output = 800 tokens total
    const estimatedCostUSD = (500 / 1000) * inputCost + (300 / 1000) * outputCost;
    return Math.max(1, Math.round(estimatedCostUSD * 1000));
  };

  const getProviderBadgeColor = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'openai': return 'bg-green-100 text-green-800 border-green-200';
      case 'google': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'deepseek': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const changeCount = Object.keys(pendingChanges).length;

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center gap-2 text-gray-600">
          <RefreshCw className="w-4 h-4 animate-spin" />
          Cargando precios de modelos desde el backend...
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Gestión de Precios de Modelos</h1>
          <p className="text-gray-600">
            Administra los precios de los modelos de IA para el cálculo de BytTokens
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Recargar
          </Button>
          
          <Button
            onClick={saveChanges}
            disabled={saving || changeCount === 0}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Save className="w-4 h-4 mr-2" />
            {saving ? 'Guardando...' : `Guardar Cambios ${changeCount > 0 ? `(${changeCount})` : ''}`}
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {changeCount > 0 && (
        <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded">
          <div className="flex items-center gap-2">
            <Edit3 className="h-4 w-4" />
            <span>Tienes {changeCount} modelo(s) con cambios sin guardar. No olvides hacer clic en "Guardar Cambios".</span>
          </div>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="w-5 h-5" />
            {usingFallback ? 'Modelos de IA - Datos de Demostración (Editables)' : 'Modelos de IA - Datos Reales del Backend (Editables)'}
            {usingFallback && (
              <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 border">
                Fallback
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {modelPricing.map((model) => {
              const hasChanges = pendingChanges[model.id];
              const currentInputCost = getCurrentValue(model, 'input_cost_per_1k');
              const currentOutputCost = getCurrentValue(model, 'output_cost_per_1k');
              
              return (
                <div key={model.id} className={`grid grid-cols-1 lg:grid-cols-6 gap-4 p-4 border rounded-lg ${hasChanges ? 'border-blue-300 bg-blue-50' : ''}`}>
                  {/* Nombre del modelo */}
                  <div className="lg:col-span-2">
                    <div className="font-medium flex items-center gap-2">
                      {model.display_name}
                      {hasChanges && <Edit3 className="w-3 h-3 text-blue-600" />}
                    </div>
                    <Badge className={`border ${getProviderBadgeColor(model.provider)} text-xs mt-1`}>
                      {model.provider.toUpperCase()}
                    </Badge>
                  </div>

                  {/* Precio Input - EDITABLE */}
                  <div>
                    <Label htmlFor={`input-${model.id}`} className="text-xs">
                      Precio Input (por 1K tokens)
                    </Label>
                    <div className="flex items-center">
                      <DollarSign className="w-3 h-3 text-gray-500 mr-1" />
                      <Input
                        id={`input-${model.id}`}
                        type="number"
                        step="0.000001"
                        value={currentInputCost}
                        onChange={(e) => handlePriceChange(model.id, 'input_cost_per_1k', e.target.value)}
                        className={`text-sm ${hasChanges ? 'border-blue-300' : ''}`}
                      />
                    </div>
                  </div>

                  {/* Precio Output - EDITABLE */}
                  <div>
                    <Label htmlFor={`output-${model.id}`} className="text-xs">
                      Precio Output (por 1K tokens)
                    </Label>
                    <div className="flex items-center">
                      <DollarSign className="w-3 h-3 text-gray-500 mr-1" />
                      <Input
                        id={`output-${model.id}`}
                        type="number"
                        step="0.000001"
                        value={currentOutputCost}
                        onChange={(e) => handlePriceChange(model.id, 'output_cost_per_1k', e.target.value)}
                        className={`text-sm ${hasChanges ? 'border-blue-300' : ''}`}
                      />
                    </div>
                  </div>

                  {/* BytTokens - ACTUALIZACIÓN EN TIEMPO REAL */}
                  <div>
                    <Label className="text-xs">BytTokens/consulta</Label>
                    <div className={`text-sm font-mono px-2 py-1 rounded text-center ${hasChanges ? 'bg-blue-100 border border-blue-200' : 'bg-gray-100'}`}>
                      ~{calculateBytokens(currentInputCost, currentOutputCost)}
                    </div>
                  </div>

                  {/* Estado y última actualización */}
                  <div>
                    <Label className="text-xs">Estado</Label>
                    <div className="space-y-1">
                      <Badge 
                        variant={model.is_active ? "default" : "secondary"}
                        className={model.is_active ? "bg-green-100 text-green-800" : ""}
                      >
                        {model.is_active ? 'Activo' : 'Inactivo'}
                      </Badge>
                      {model.updated_by && (
                        <div className="text-xs text-gray-500 mt-1">
                          Por: {model.updated_by}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="text-center py-6">
          <DollarSign className="w-12 h-12 mx-auto text-gray-400 mb-2" />
          <p className="text-gray-600">
            {usingFallback 
              ? '⚠️ Modo edición local. Los cambios se guardan temporalmente.' 
              : '✅ Modo edición completo. Los cambios se sincronizan con el backend.'
            }
          </p>
          <p className="text-sm text-gray-500 mt-2">
            {changeCount > 0 
              ? `${changeCount} cambio(s) pendiente(s). Haz clic en "Guardar Cambios" para aplicar.`
              : 'Edita los precios y verás los BytTokens actualizarse en tiempo real.'
            }
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default ModelPricingPage; 