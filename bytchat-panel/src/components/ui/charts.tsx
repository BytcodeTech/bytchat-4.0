import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './card';

// Componente de gráfico de barras simple
interface BarChartProps {
  data: Array<{ label: string; value: number; color?: string }>;
  title: string;
  maxValue?: number;
}

export const SimpleBarChart: React.FC<BarChartProps> = ({ data, title, maxValue }) => {
  const max = maxValue || Math.max(...data.map(d => d.value));
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {data.map((item, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className="w-20 text-sm text-right text-muted-foreground">
                {item.label}
              </div>
              <div className="flex-1 bg-gray-200 rounded-full h-3 relative">
                <div
                  className={`h-3 rounded-full transition-all duration-500 ${
                    item.color || 'bg-blue-500'
                  }`}
                  style={{ width: `${(item.value / max) * 100}%` }}
                />
              </div>
              <div className="w-16 text-sm font-medium text-right">
                {item.value.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Componente de gráfico de barras verticales para actividad diaria
interface DailyActivityBarChartProps {
  data: Array<{ date: string; value: number }>;
  title: string;
}

export const DailyActivityBarChart: React.FC<DailyActivityBarChartProps> = ({ data, title }) => {
  const maxValue = Math.max(...data.map(d => d.value)) || 1;
  
  // Función para formatear la fecha a día/mes
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const day = date.getDate();
    const month = date.getMonth() + 1;
    return `${day}/${month}`;
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-48 flex items-end justify-center gap-6 p-4">
          {data.map((item, index) => (
            <div key={index} className="flex flex-col items-center group">
              {/* Barra vertical */}
              <div className="relative flex flex-col justify-end h-32 mb-2">
                <div
                  className="bg-blue-500 rounded-t-md min-h-[4px] w-8 transition-all duration-500 hover:bg-blue-600 group-hover:bg-blue-600"
                  style={{ 
                    height: `${Math.max((item.value / maxValue) * 100, 4)}%`,
                  }}
                />
                {/* Tooltip con valor */}
                <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                  {item.value.toLocaleString()} tokens
                </div>
              </div>
              
              {/* Etiqueta de fecha */}
              <div className="text-xs text-gray-600 text-center">
                {formatDate(item.date)}
              </div>
            </div>
          ))}
        </div>
        
        {/* Eje Y con valores de referencia */}
        <div className="flex justify-between text-xs text-gray-500 mt-2 px-4">
          <span>0</span>
          <span className="text-center">Tokens por día</span>
          <span>{maxValue.toLocaleString()}</span>
        </div>
      </CardContent>
    </Card>
  );
};

// Componente de gráfico de línea simple
interface LineChartProps {
  data: Array<{ date: string; value: number }>;
  title: string;
  color?: string;
}

export const SimpleLineChart: React.FC<LineChartProps> = ({ data, title, color = 'blue' }) => {
  const maxValue = Math.max(...data.map(d => d.value));
  const minValue = Math.min(...data.map(d => d.value));
  const range = maxValue - minValue || 1;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-48 relative">
          <svg width="100%" height="100%" className="overflow-visible">
            {/* Grid lines */}
            {[0, 25, 50, 75, 100].map(y => (
              <line
                key={y}
                x1="0"
                y1={`${y}%`}
                x2="100%"
                y2={`${y}%`}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
            ))}
            
            {/* Data line */}
            <polyline
              fill="none"
              stroke={color === 'blue' ? '#3b82f6' : color === 'green' ? '#10b981' : '#f59e0b'}
              strokeWidth="2"
              points={data.map((point, index) => {
                const x = (index / (data.length - 1)) * 100;
                const y = 100 - ((point.value - minValue) / range) * 100;
                return `${x},${y}`;
              }).join(' ')}
            />
            
            {/* Data points */}
            {data.map((point, index) => {
              const x = (index / (data.length - 1)) * 100;
              const y = 100 - ((point.value - minValue) / range) * 100;
              return (
                <circle
                  key={index}
                  cx={`${x}%`}
                  cy={`${y}%`}
                  r="3"
                  fill={color === 'blue' ? '#3b82f6' : color === 'green' ? '#10b981' : '#f59e0b'}
                />
              );
            })}
          </svg>
          
          {/* X-axis labels */}
          <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-muted-foreground">
            {data.map((point, index) => (
              <span key={index} className={index === 0 ? 'text-left' : index === data.length - 1 ? 'text-right' : 'text-center'}>
                {new Date(point.date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' })}
              </span>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Componente de gráfico circular (donut)
interface DonutChartProps {
  data: Array<{ label: string; value: number; color: string }>;
  title: string;
  centerText?: string;
}

export const DonutChart: React.FC<DonutChartProps> = ({ data, title, centerText }) => {
  const total = data.reduce((sum, item) => sum + item.value, 0);
  let cumulativePercentage = 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center">
        <div className="relative w-48 h-48">
          <svg width="192" height="192" className="transform -rotate-90">
            {data.map((segment, index) => {
              const percentage = (segment.value / total) * 100;
              const strokeDasharray = `${percentage * 2.51} 251`;
              const strokeDashoffset = -cumulativePercentage * 2.51;
              cumulativePercentage += percentage;

              return (
                <circle
                  key={index}
                  cx="96"
                  cy="96"
                  r="40"
                  fill="transparent"
                  stroke={segment.color}
                  strokeWidth="16"
                  strokeDasharray={strokeDasharray}
                  strokeDashoffset={strokeDashoffset}
                  className="transition-all duration-1000"
                />
              );
            })}
          </svg>
          {centerText && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-2xl font-bold">{centerText}</div>
                <div className="text-sm text-muted-foreground">Total</div>
              </div>
            </div>
          )}
        </div>
        
        {/* Legend */}
        <div className="mt-4 space-y-2">
          {data.map((item, index) => (
            <div key={index} className="flex items-center space-x-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm">{item.label}</span>
              <span className="text-sm text-muted-foreground">
                ({((item.value / total) * 100).toFixed(1)}%)
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Componente de métrica destacada
interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'yellow' | 'red';
}

export const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  subtitle, 
  trend, 
  icon, 
  color = 'blue' 
}) => {
  const colorClasses = {
    blue: 'border-blue-200 bg-blue-50',
    green: 'border-green-200 bg-green-50',
    yellow: 'border-yellow-200 bg-yellow-50',
    red: 'border-red-200 bg-red-50',
  };

  return (
    <Card className={`${colorClasses[color]} border-l-4`}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {subtitle && (
              <p className="text-sm text-muted-foreground">{subtitle}</p>
            )}
            {trend && (
              <div className={`flex items-center mt-2 text-sm ${
                trend.isPositive ? 'text-green-600' : 'text-red-600'
              }`}>
                <span>{trend.isPositive ? '↗' : '↘'}</span>
                <span className="ml-1">{Math.abs(trend.value)}%</span>
              </div>
            )}
          </div>
          {icon && (
            <div className="text-2xl opacity-60">
              {icon}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}; 