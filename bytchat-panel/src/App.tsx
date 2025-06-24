import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "./store/authStore";

const App = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  // Si el usuario no está autenticado, redirige a la página de login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Si está autenticado, muestra la página solicitada (el Dashboard)
  return <Outlet />;
};

export default App;