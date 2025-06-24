import Header from '@/components/layout/Header';
import Sidebar from '@/components/layout/Sidebar';

const DashboardPage = () => {
  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 p-6 md:p-8 lg:p-10">
          <h1 className="text-2xl font-semibold text-slate-800">
            Bienvenido al Panel de Bytchat
          </h1>
          <p className="mt-2 text-slate-600">
            Selecciona una opción del menú lateral para comenzar.
          </p>
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;