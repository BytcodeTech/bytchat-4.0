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

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        path: 'dashboard', // <-- 2. AÑADIMOS UNA RUTA ESPECÍFICA
        element: <DashboardPage />,
      },
      {
        path: 'bots', // <-- 3. AÑADIMOS LA RUTA PARA LOS BOTS
        element: <BotsPage />,
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