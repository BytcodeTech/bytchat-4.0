// bytchat-panel/src/pages/AnalyticsPage.tsx

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3 } from "lucide-react"; // 1. Importamos el ícono desde 'lucide-react'

const AnalyticsPage = () => {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-3xl font-bold tracking-tight">Analíticas</h1>
      <div className="flex-1">
        <Card className="h-full">
          <CardHeader>
            <CardTitle>Métricas de Uso y Rendimiento</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center text-center gap-4 py-16">
              {/* 2. Usamos el ícono importado */}
              <BarChart3 className="w-16 h-16 text-slate-400" />
              <h2 className="text-2xl font-semibold">Próximamente</h2>
              <p className="text-muted-foreground max-w-md">
                Estamos trabajando para traerte métricas detalladas sobre el
                rendimiento y el uso de tus bots. ¡Vuelve pronto!
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AnalyticsPage;