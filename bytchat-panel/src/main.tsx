import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import LoginPage from './pages/LoginPage.tsx';
import DashboardPage from './pages/DashboardPage.tsx';

// Definición de las rutas de la aplicación
const router = createBrowserRouter([
  {
    path: '/',
    element: <App />, // Elemento principal que protege las rutas anidadas
    children: [
      {
        path: '/', // Ruta principal (dashboard)
        element: <DashboardPage />,
      },
      // Aquí puedes añadir más rutas protegidas en el futuro
    ],
  },
  {
    path: '/login',
    element: <LoginPage />, // Ruta de login es pública
  },
]);


ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)