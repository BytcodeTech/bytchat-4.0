import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "./store/authStore";
import Sidebar from "./components/layout/Sidebar";
import Header from "./components/layout/Header";

const App = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Si está autenticado, muestra la plantilla principal del panel.
  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar />
      {/* --- EL CAMBIO ESTÁ EN ESTA LÍNEA --- */}
      {/* Quitamos la clase 'overflow-hidden' para permitir que el contenido se expanda */}
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto bg-slate-100 p-6 md:p-8 lg:p-10">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default App;