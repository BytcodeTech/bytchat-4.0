// bytchat-panel/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import LoginPage from './pages/LoginPage.tsx';
import DashboardPage from './pages/DashboardPage.tsx';
import RegisterPage from './pages/RegisterPage.tsx';
import BotsPage from './pages/BotsPage.tsx'; // <-- 1. IMPORTAR LA NUEVA PÁGINA
import TrainingPage from './pages/TrainingPage'; // <-- Importar la nueva página
import EmbedChatPage from './pages/EmbedChatPage'; // Importar la nueva página
import AnalyticsPage from './pages/AnalyticsPage'; // Importar la página de analíticas
import BillingPage from './pages/BillingPage'; // Importar la página de facturación
import AdminPage from './pages/AdminPage';
import ModelPricingPage from './pages/ModelPricingPage'; // Reactivado con versión simplificada
import AdminRoute from './components/auth/AdminRoute';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true, // <-- Ruta por defecto
        element: <BotsPage />,
      },
      {
        path: 'dashboard', // <-- 2. AÑADIMOS UNA RUTA ESPECÍFICA
        element: <DashboardPage />,
      },
      {
        path: 'bots', // <-- 3. AÑADIMOS LA RUTA PARA LOS BOTS
        element: <BotsPage />,
      },
      {
        path: 'training', // <-- Añadir la ruta de entrenamiento
        element: <TrainingPage />, 
      },
      {
        path: 'embed-chat',
        element: <EmbedChatPage />,
      },
      {
        path: 'analytics', // <-- Añadir la ruta de analíticas
        element: <AnalyticsPage />,
      },
      {
        path: 'billing', // <-- Añadir la ruta de facturación
        element: <BillingPage />,
      },
      {
        path: 'admin',
        element: (
          <AdminRoute>
            <AdminPage />
          </AdminRoute>
        ),
      },
      {
        path: 'model-pricing',
        element: (
          <AdminRoute>
            <ModelPricingPage />
          </AdminRoute>
        ),
      },
      {
        index: true, // <-- 4. REDIRIGIMOS LA RUTA RAÍZ A /bots
        element: <BotsPage />,
      },
    ],
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);