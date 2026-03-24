import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";

export default function GuidePage() {
  return (
    <ProtectedRoute>
      <Layout>
        <div className="max-w-4xl">
          <h1 className="mb-6 text-3xl font-bold text-gray-900">Guia de Usuario</h1>
          <div className="space-y-4 rounded-xl bg-white p-6 shadow">
            <p>1. Ve a Configuracion para crear busquedas y URLs del sitio.</p>
            <p>2. En Dashboard selecciona una busqueda activa y actualiza anuncios.</p>
            <p>3. Usa favoritos para marcar publicaciones importantes.</p>
            <p>4. Revisa Logs para monitorear eventos y errores del scraper.</p>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
}
