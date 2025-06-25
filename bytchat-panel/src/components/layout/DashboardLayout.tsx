import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

// Definimos el tipo de las props, en este caso 'children'
// que será el contenido de la página a mostrar.
interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-slate-50">
      {/* La barra lateral fija a la izquierda */}
      <Sidebar />
      
      {/* El contenedor principal que se expande */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* La cabecera en la parte superior */}
        <Header />
        
        {/* El contenido principal de la página */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-100 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;