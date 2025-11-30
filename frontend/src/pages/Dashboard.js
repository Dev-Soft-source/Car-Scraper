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

  const [running, setRunning] = useState(false);
  const [stopping, setStopping] = useState(true);
  const isStart = useRef(false);

  const hasFetchedSearches = useRef(false);

  // Ask for notifications permission
  useEffect(() => {
    if(!isStart.current){
      isStart.current = true;
      requestNotificationPermission();
      fetchStats();
      const interval = setInterval(fetchStats, 7000);
      return () => clearInterval(interval);
    }      
  }, []);

  const fetchStats = async () => {
    try {
      const response = await searchService.getState();
      if (response.data.running){
        setRunning(true);
        setStopping(false);
      }else
      {
        setRunning(false);
        setStopping(true);
      }
      // setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      // setLoading(false);
    }
  };

  // Fetch searches
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

  // Fetch listings
  const fetchListings = useCallback(async () => {
    
    if (!activeSearch) return;
    
    setLoading(true);
    try {
      const response = await listingService.getListingsBySearch(activeSearch, filters);
      const newListings = response.data;

      // Notification for new "below target" listings
      if (listings.length > 0) {
        const newBelowTarget = newListings.filter(
          nl => nl.target_price_met && !listings.find(ol => ol.id === nl.id)
        );

        if (newBelowTarget.length > 0) {
          
          newBelowTarget.forEach(listing => {
            showNotification('New Listing Below Target!', {
              body: `${listing.title || listing.description} - €${listing.price}`,
              icon: '/favicon.ico',
            });
          });
          toast.success(`${newBelowTarget.length} ¡nuevo(s) anuncio(s) por debajo del precio objetivo!`);
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
  }, [activeSearch, filters, listings]);

  // Filter logic
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

    // Sorting
    const sortBy = currentFilters.sort;
    if (sortBy) {
      const sorters = {
        'price_asc': (a, b) => a.price - b.price,
        'price_desc': (a, b) => b.price - a.price,
        'date_desc': (a, b) => new Date(b.last_updated) - new Date(a.last_updated),
        'date_asc': (a, b) => new Date(a.last_updated) - new Date(b.last_updated),
      };
      filtered.sort(sorters[sortBy]);
    }

    setFilteredListings(filtered);
  };

  // Fetch searches only once
  useEffect(() => {
    if (!hasFetchedSearches.current) {
      fetchSearches();
      hasFetchedSearches.current = true;
    }
  }, []);

  useEffect(() => { fetchListings(); }, [activeSearch]);

  // Auto-refresh every 30s when scraper is running
  useEffect(() => {
    if (running) {
      const interval = setInterval(fetchListings, 600000);
      return () => clearInterval(interval);
    }
  }, [running, fetchListings]);

  // Re-filter on filter change
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

  // 🔥 START/STOP SCRAPER BUTTON DISABLED UNTIL RESPONSE
  const handleStart = async () => {
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
      setRunning(false); // re-enable button
    }
  };

  const handleStop = async () => {
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
      setStopping(false); // re-enable button
    }
  };

  const clearFilters = () => setFilters({});

  return (
    <div data-testid="dashboard-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Panel</h1>
          <p className="text-gray-600 mt-1">
            Monitorear y analizar los anuncios de Wallapop
          </p>
        </div>

        <div className="flex items-center space-x-3">          

          {/* Start/Stop Scraper */}
          <button
            onClick={handleStop}
            data-testid="start-stop-button"
            disabled={!stopping || running}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-semibold transition-all transform 
              ${
                 running
                  ? "opacity-50 cursor-not-allowed"
                  : "hover:scale-105"
              }
              ${
                "bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white"
              }`}
          >
            {running ? (
              <>
                <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full">
                  {" "}
                </div>
                <span>Procesando...</span>
              </>
            ) : (
              <>
                <Play size={20} />
                <span>Iniciar el rastreador</span>
              </>
            )}
          </button>

          <button
            onClick={handleStart}
            data-testid="start-stop-button"
            disabled={stopping || !running}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-semibold transition-all transform 
              ${
                stopping
                  ? "opacity-50 cursor-not-allowed"
                  : "hover:scale-105"
              }
              ${
                "bg-red-500 hover:bg-red-600 text-white"
              }`}
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

          {/* Refresh */}
          <button
            onClick={fetchListings}
            data-testid="refresh-button"
            className="p-3 bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-lg transition-all"
            disabled={loading}
          >
            <RefreshCw size={20} className={loading ? "animate-spin" : ""} />
          </button>

          {/* Charts toggle */}
          <button
            onClick={() => setShowCharts(!showCharts)}
            data-testid="toggle-charts-button"
            className={`flex items-center space-x-2 px-4 py-3 rounded-lg font-semibold transition-all 
              ${
                showCharts
                  ? "bg-purple-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }
            `}
          >
            <BarChart3 size={20} />
            <span>Gráficos</span>
          </button>
        </div>
      </div>

      {/* Searches */}
      {searches.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-4 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Búsqueda activa
          </label>
          <select
            value={activeSearch || ""}
            onChange={(e) => setActiveSearch(e.target.value)}
            data-testid="search-selector"
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
      <FilterPanel
        filters={filters}
        setFilters={setFilters}
        onClear={clearFilters}
      />

      {/* Charts */}
      {showCharts && filteredListings.length > 0 && (
        <ListingCharts listings={filteredListings} />
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-600 rounded-xl p-6 text-white shadow-lg">
          <div className="text-sm opacity-90">Total de anuncios</div>
          <div className="text-3xl font-bold mt-2" data-testid="total-listings">
            {filteredListings.length}
          </div>
        </div>

        <div className="bg-green-600 rounded-xl p-6 text-white shadow-lg">
          <div className="text-sm opacity-90">Por debajo del objetivo</div>
          <div
            className="text-3xl font-bold mt-2"
            data-testid="below-target-count"
          >
            {filteredListings.filter((l) => l.target_price_met).length}
          </div>
        </div>

        <div className="bg-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="text-sm opacity-90">Favoritos</div>
          <div
            className="text-3xl font-bold mt-2"
            data-testid="favorites-count"
          >
            {filteredListings.filter((l) => l.is_favorite).length}
          </div>
        </div>

        <div className="bg-orange-600 rounded-xl p-6 text-white shadow-lg">
          <div className="text-sm opacity-90">Precio promedio</div>
          <div className="text-3xl font-bold mt-2" data-testid="avg-price">
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredListings.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredListings.map((listing) => (
            <ListingCard
              key={listing.id}
              listing={listing}
              onToggleFavorite={handleToggleFavorite}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">📦</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            No se encontraron anuncios
          </h3>
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
