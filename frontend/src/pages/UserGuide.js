import React from 'react';
import { Settings, Play, Filter, BarChart3, Bell } from 'lucide-react';

const UserGuide = () => {
  return (
    <div data-testid="user-guide-page" className="max-w-4xl">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Guía de Usuario</h1>

      <div className="space-y-6">
        {/* Introduction */}
        <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <h2 className="text-2xl font-bold mb-3">¡Bienvenido a Wallapop Scraper!</h2>
          <p className="text-blue-100">
            Esta aplicación extrae automáticamente anuncios de Wallapop según tus criterios y te avisa cuando
            los artículos están por debajo de tu precio objetivo. Sigue esta guía para comenzar.
          </p>
        </div>

        {/* Getting Started */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-xl font-bold text-blue-600">1</span>
            </div>
            <h2 className="text-xl font-bold text-gray-900">Configura tu búsqueda</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Navega a <strong>Configuración</strong> y crea una nueva búsqueda:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li>Ponle un nombre descriptivo</li>
              <li>Especifica criterios: marca, modelo, rango de años, precio, ubicación, etc.</li>
              <li>Establece tu <strong>precio objetivo</strong> — recibirás alertas cuando los anuncios estén por debajo</li>
              <li>Elige si quieres rastrear vendedores particulares, profesionales o ambos</li>
              <li>Marca la búsqueda como activa para incluirla en el scraping</li>
            </ul>
          </div>
        </div>

        {/* Scraping Settings */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Settings className="text-purple-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Configura los ajustes de scraping</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>En la página de <strong>Configuración</strong>, define:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li><strong>Intervalo de scraping:</strong> frecuencia de revisión (en horas)</li>
              <li><strong>Palabras clave:</strong> términos generales para filtrar anuncios</li>
              <li><strong>Rango de precios:</strong> precio mínimo y máximo</li>
              <li><strong>URLs del sitio:</strong> añade URLs de Wallapop u otros marketplaces</li>
            </ul>
          </div>
        </div>

        {/* Start Scraping */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Play className="text-green-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Iniciar el scraping</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>En el <strong>Dashboard</strong>:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li>Selecciona una búsqueda activa en el menú desplegable</li>
              <li>Haz clic en <strong>Start Scraper</strong> para comenzar</li>
              <li>El scraper se ejecuta en segundo plano según el intervalo configurado</li>
              <li>Haz clic en <strong>Stop Scraper</strong> para pausar</li>
              <li>Usa el botón <strong>Refresh</strong> para actualizar manualmente</li>
            </ul>
          </div>
        </div>

        {/* Filtering & Sorting */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Filter className="text-orange-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Filtrar y ordenar resultados</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Usa el panel de filtros para refinar tus resultados:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li><strong>Buscar:</strong> Encuentra anuncios por palabra clave</li>
              <li><strong>Marca/Modelo:</strong> Filtra por marca y modelo</li>
              <li><strong>Precio:</strong> Define precio mínimo y máximo</li>
              <li><strong>Ubicación:</strong> Filtra por zona geográfica</li>
              <li><strong>Tipo de vendedor:</strong> Particular o profesional</li>
              <li><strong>Solo por debajo del precio objetivo</strong></li>
              <li><strong>Ordenar:</strong> Por precio o fecha (más nuevo/más antiguo)</li>
            </ul>
          </div>
        </div>

        {/* Alerts */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <Bell className="text-red-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Alertas y notificaciones</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Recibe avisos cuando aparezcan buenas ofertas:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li>Anuncios por debajo del precio objetivo se marcan en verde</li>
              <li>Suena una alerta cuando aparecen nuevas ofertas</li>
              <li>Notificaciones del navegador (actívalas)</li>
              <li>Revisa el dashboard regularmente</li>
            </ul>
          </div>
        </div>

        {/* Data Analysis */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="text-indigo-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Analiza los datos de precios</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Haz clic en <strong>Charts</strong> para ver:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li><strong>Distribución de precios:</strong> Cómo se reparten los anuncios</li>
              <li><strong>Precio medio por año:</strong> Relación entre año y precio</li>
              <li><strong>Kilometraje vs precio:</strong> Relación entre uso y valor</li>
              <li>Utiliza esta información para ajustar mejores precios objetivo</li>
            </ul>
          </div>
        </div>

        {/* Favorites */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-pink-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">❤️</span>
            </div>
            <h2 className="text-xl font-bold text-gray-900">Gestionar favoritos</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Haz seguimiento de los anuncios interesantes:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li>Haz clic en el corazón para añadir un anuncio a favoritos</li>
              <li>Consulta el número de favoritos en el dashboard</li>
              <li>Filtra para ver solo tus favoritos</li>
            </ul>
          </div>
        </div>

        {/* Logs */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span className="text-xl font-bold text-yellow-600">📄</span>
            </div>
            <h2 className="text-xl font-bold text-gray-900">Ver registro de actividad</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Supervisa la actividad en la página <strong>Logs</strong>:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li>Inicio y fin de sesiones de scraping</li>
              <li>Número de anuncios encontrados</li>
              <li>Errores o advertencias</li>
              <li>Filtrar por nivel (info, success, warning, error)</li>
            </ul>
          </div>
        </div>

        {/* Tips */}
        <div className="bg-gradient-to-br from-green-500 to-teal-600 rounded-xl p-6 text-white shadow-lg">
          <h2 className="text-2xl font-bold mb-3">💡 Consejos útiles</h2>
          <ul className="space-y-2 text-green-100">
            <li>• Crea varias búsquedas para diferentes vehículos o rangos de precios</li>
            <li>• Ajusta precios objetivo basándote en los datos de los gráficos</li>
            <li>• Usa intervalos más cortos en horas pico</li>
            <li>• Activa las notificaciones del navegador</li>
            <li>• Revisa los registros para verificar que todo funcione bien</li>
            <li>• Guarda anuncios interesantes en favoritos</li>
          </ul>
        </div>

        {/* Support */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-3">¿Necesitas ayuda?</h2>
          <p className="text-gray-700">
            Si tienes problemas o preguntas, revisa la página de Logs para ver los detalles
            o contacta con soporte. ¡Felices búsquedas!
          </p>
        </div>
      </div>
    </div>
  );
};

export default UserGuide;
