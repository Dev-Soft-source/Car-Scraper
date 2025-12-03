import React, { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'react-toastify';
import listingService from '../services/listing.service';
import searchService from '../services/search.service';
import ListingCard from '../components/ListingCard';
import FilterPanel from '../components/FilterPanel';
import ListingCharts from '../components/ListingCharts';
import { Play, Square, RefreshCw, BarChart3 } from 'lucide-react';
import { playAlertSound, showNotification, requestNotificationPermission } from '../utils/soundAlert';

const Dashboard = () => {
  const [listings, setListings] = useState([]);
  const [filteredListings, setFilteredListings] = useState([]);
  const [searches, setSearches] = useState([]);
  const [activeSearch, setActiveSearch] = useState(null);
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(false);
  const [showCharts, setShowCharts] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  const [running, setRunning] = useState(false);
  const [stopping, setStopping] = useState(true);
  const isStart = useRef(false);

  const hasFetchedSearches = useRef(false);

  // Request notifications on first load
  useEffect(() => {
    if (!isStart.current) {
      
      requestNotificationPermission();
      fetchStats();``
      const interval = setInterval(fetchStats, 7000);
      return () => clearInterval(interval);
      isStart.current = true;
    }
  }, []);

  const fetchStats = async () => {
    try {
      const response = await searchService.getState();
      if (response.data.running) {
        setRunning(true);
        setStopping(false);
      } else {
        setRunning(false);
        setStopping(true);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchSearches = async () => {
    try {
      const response = await searchService.getAllSearches();
      setSearches(response.data);

      if (response.data.length > 0 && !activeSearch) {
        setActiveSearch(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching searches:', error);
      toast.error('Error al obtener las búsquedas');
    }
  };

  const fetchListings = useCallback(
    async () => {
      if (!activeSearch) return;

      setLoading(true);
      try {
        const response = await listingService.getListingsBySearch(activeSearch, filters);
        const newListings = response.data;

        // Notification for new below-target listings
        if (listings.length > 0) {
          const newBelow = newListings.filter(
            nl => nl.target_price_met && !listings.find(ol => ol.id === nl.id)
          );

          if (newBelow.length > 0) {
            newBelow.forEach(listing => {
              showNotification('New Listing Below Target!', {
                body: `${listing.title || listing.description} - €${listing.price}`,
                icon: '/favicon.ico',
              });
            });
            toast.success(`${newBelow.length} ¡nuevo(s) anuncio(s) por debajo del precio objetivo!`);
          }
        }

        setListings(newListings);
        applyFilters(newListings, filters);
      } catch (error) {
        console.error('Error fetching listings:', error);
        toast.error('Error al obtener los anuncios');
      } finally {
        setLoading(false);
      }
    },
    [activeSearch, filters, listings]
  );

  const applyFilters = (data, currentFilters) => {
    let filtered = [...data];

    const contains = (value, search) =>
      (value || '').toLowerCase().includes(search.toLowerCase());

    if (currentFilters.search) {
      filtered = filtered.filter(l =>
        contains(l.title || l.description, currentFilters.search) ||
        contains(l.make, currentFilters.search) ||
        contains(l.model, currentFilters.search)
      );
    }

    if (currentFilters.make) {
      filtered = filtered.filter(l => contains(l.make, currentFilters.make));
    }

    if (currentFilters.model) {
      filtered = filtered.filter(l => contains(l.model, currentFilters.model));
    }

    if (currentFilters.location) {
      filtered = filtered.filter(l => contains(l.location, currentFilters.location));
    }

    if (currentFilters.min_price) {
      filtered = filtered.filter(l => l.price >= Number(currentFilters.min_price));
    }

    if (currentFilters.max_price) {
      filtered = filtered.filter(l => l.price <= Number(currentFilters.max_price));
    }

    if (currentFilters.seller_type) {
      filtered = filtered.filter(l => l.seller_type === currentFilters.seller_type);
    }

    if (currentFilters.target_price_only) {
      filtered = filtered.filter(l => l.target_price_met);
    }

    if (currentFilters.showOnlyBelowTarget) {
      filtered = filtered.filter(l => l.target_price_met);
    }

    if (currentFilters.onlyFavorites) {
      filtered = filtered.filter(l => l.is_favorite);
    }

    if (currentFilters.sort) {
      const sorters = {
        'price_asc': (a, b) => a.price - b.price,
        'price_desc': (a, b) => b.price - a.price,
        'date_desc': (a, b) => new Date(b.last_updated) - new Date(a.last_updated),
        'date_asc': (a, b) => new Date(a.last_updated) - new Date(b.last_updated),
      };
      filtered.sort(sorters[currentFilters.sort]);
    }

    setFilteredListings(filtered);
  };

  useEffect(() => {
    if (!hasFetchedSearches.current) {
      fetchSearches();
      hasFetchedSearches.current = true;
    }
  }, []);

  useEffect(() => { fetchListings(); }, [activeSearch]);

  useEffect(() => {
    if (running) {
      const interval = setInterval(fetchListings, 600000);
      return () => clearInterval(interval);
    }
  }, [running, fetchListings]);

  useEffect(() => applyFilters(listings, filters), [filters, listings]);

  const handleToggleFavorite = async (listingId) => {
    try {
      await listingService.toggleFavorite(listingId);
      setListings(prev =>
        prev.map(l => l.id === listingId ? { ...l, is_favorite: !l.is_favorite } : l)
      );
      toast.success('Favorito actualizado');
    } catch {
      toast.error('Error al actualizar el favorito');
    }
  };

  // Stop
  const handleStop = async () => {
    console.log("sldfkjsadlfjsdljfjsadlfkjsdlfkjsadlfjsdlfj: ", activeSearch);
    if (!activeSearch) {
      toast.error('Por favor, selecciona primero una búsqueda');
      return;
    }
    setRunning(true);
    try {
      await searchService.stopSearch(activeSearch);
      toast.info('Rastreador detenido');
    } catch {
      toast.error('Error al iniciar/detener el rastreador');
    } finally {
      setRunning(false);
    }
  };

  // Start
  const handleStart = async () => {
    console.log("sldfkjsadlfjsdljfjsadlfkjsdlfkjsadlfjsdlfj: ", activeSearch);
    setStopping(true);
    try {
      await searchService.startSearch(activeSearch);
      playAlertSound();
      setRunning(false);
      toast.success('Rastreador iniciado');
      fetchListings();
    } catch {
      toast.error('Error al iniciar/detener el rastreador');
    } finally {
      setStopping(false);
    }
  };

  const clearFilters = () => setFilters({});
  const showAllListings = () => setFilters(prev => ({ ...prev, showOnlyBelowTarget: false, onlyFavorites: false }));
  const showBelowTarget = () => setFilters(prev => ({ ...prev, showOnlyBelowTarget: true, onlyFavorites: false }));
  const showFavoritesOnly = () => setFilters(prev => ({ ...prev, onlyFavorites: true, showOnlyBelowTarget: false }));

  return (
    <div data-testid="dashboard-page">

      {/* 🔥 Sticky + Blurred Header */}
      <div className="sticky top-0 z-50 backdrop-blur-md pb-4 mb-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Panel</h1>
            <p className="text-gray-600 mt-1">
              Monitorear y analizar los anuncios de Wallapop
            </p>
          </div>

          <div className="flex items-center space-x-3">

            {/* Start */}
            <button
              onClick={handleStart}
              disabled={!stopping || running}
              className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-semibold transition-all transform 
                ${running ? "opacity-50 cursor-not-allowed" : "hover:scale-105"}
                bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white`}
            >
              {running ? (
                <>
                  <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                  <span>Procesando...</span>
                </>
              ) : (
                <>
                  <Play size={20} />
                  <span>Iniciar el rastreador</span>
                </>
              )}
            </button>

            {/* Stop */}
            <button
              onClick={handleStop}
              disabled={stopping || !running}
              className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-semibold transition-all transform 
                ${stopping ? "opacity-50 cursor-not-allowed" : "hover:scale-105"}
                bg-red-500 hover:bg-red-600 text-white`}
            >
              {stopping ? (
                <>
                  <Square size={20} />
                  <span>Procesando...</span>
                </>
              ) : (
                <>
                  <Square size={20} />
                  <span>Detener el rastreador</span>
                </>
              )}
            </button>

            <button
              onClick={fetchListings}
              className="p-3 bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-lg transition-all"
              disabled={loading}
            >
              <RefreshCw size={20} className={loading ? "animate-spin" : ""} />
            </button>

            <button
              onClick={() => setShowCharts(!showCharts)}
              className={`flex items-center space-x-2 px-4 py-3 rounded-lg font-semibold transition-all 
                ${showCharts ? "bg-purple-600 text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300"}`}
            >
              <BarChart3 size={20} />
              <span>Gráficos</span>
            </button>

          </div>
        </div>
      </div>

      {/* Everything else stays EXACTLY the same... */}
      {/* Searches */}
      {searches.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-4 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Búsqueda activa
          </label>
          <select
            value={activeSearch || ""}
            onChange={(e) => setActiveSearch(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {searches.map((search) => (
              <option key={search.id} value={search.id}>
                {search.name}({search.site_url}) - {search.description}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Filter Panel */}
      <div className="bg-[#e4f5f5] rounded-xl shadow-lg mb-6 overflow-hidden">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="w-full flex items-center justify-between px-4 py-3 bg-[#38b7b7] text-left font-semibold text-gray-800 hover:bg-[#2e9797]"
        >
          <span>Filtros</span>
          <span className={`transform transition-transform ${showFilters ? "rotate-180" : "rotate-0"}`}>▾</span>
        </button>

        <div
          className={`transition-all duration-300 bg-[#a0d9db] ease-in-out ${
            showFilters ? "max-h-[1000px] opacity-100" : "max-h-0 opacity-0"
          } overflow-hidden`}
        >
          <div className="p-4 border-t">
            <FilterPanel filters={filters} setFilters={setFilters} onClear={clearFilters} />
          </div>
        </div>
      </div>

      {/* Charts */}
      {showCharts && filteredListings.length > 0 && (
        <ListingCharts listings={filteredListings} />
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div onClick={showAllListings} className="bg-blue-600 rounded-xl p-6 text-white shadow-lg cursor-pointer hover:bg-blue-700 transition">
          <div className="text-sm opacity-90">Total de anuncios</div>
          <div className="text-3xl font-bold mt-2">{filteredListings.length}</div>
        </div>

        <div onClick={showBelowTarget} className="bg-green-600 rounded-xl p-6 text-white shadow-lg cursor-pointer hover:bg-green-700 transition">
          <div className="text-sm opacity-90">Por debajo del objetivo</div>
          <div className="text-3xl font-bold mt-2">
            {filteredListings.filter(l => l.target_price_met).length}
          </div>
        </div>

        <div onClick={showFavoritesOnly} className="bg-purple-600 rounded-xl p-6 text-white shadow-lg cursor-pointer hover:bg-purple-700 transition">
          <div className="text-sm opacity-90">Favoritos</div>
          <div className="text-3xl font-bold mt-2">
            {filteredListings.filter(l => l.is_favorite).length}
          </div>
        </div>

        <div className="bg-orange-600 rounded-xl p-6 text-white shadow-lg">
          <div className="text-sm opacity-90">Precio promedio</div>
          <div className="text-3xl font-bold mt-2">
            €
            {filteredListings.length > 0
              ? Math.round(
                  filteredListings.reduce((sum, l) => sum + (l.price || 0), 0) /
                  filteredListings.length
                ).toLocaleString()
              : "0"}
          </div>
        </div>
      </div>

      {/* Listings */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
        </div>
      ) : filteredListings.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredListings.map((listing) => (
            <ListingCard key={listing.id} listing={listing} onToggleFavorite={handleToggleFavorite} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">📦</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">No se encontraron anuncios</h3>
          <p className="text-gray-600">
            {searches.length === 0
              ? "Crea una búsqueda en Configuración para comenzar a rastrear"
              : "Intenta ajustar tus filtros o iniciar el rastreador"}
          </p>
        </div>
      )}

    </div>
  );
};

export default Dashboard;
