import React, { useState, useEffect, useRef } from 'react';
import { toast } from 'react-toastify';
import logsService from '../services/logs.service';
import { format } from 'date-fns';
import { RefreshCw, AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    level: '',
    search: ''
  });

  const hasFetched = useRef(false);

  useEffect(() => {
    if(!hasFetched.current)
    {
      fetchLogs();
      hasFetched.current = true;
    }
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await logsService.getAllLogs(filters);
      setLogs(response.data);
    } catch (error) {
      console.error('Error fetching logs:', error);
      toast.error('Error al obtener los registros');
    } finally {
      setLoading(false);
    }
  };

  const getLogIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'error':
        return <XCircle className="text-red-500" size={20} />;
      case 'warning':
        return <AlertCircle className="text-yellow-500" size={20} />;
      case 'success':
        return <CheckCircle className="text-green-500" size={20} />;
      default:
        return <Info className="text-blue-500" size={20} />;
    }
  };

  const getLogColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'error':
        return 'border-l-4 border-red-500 bg-red-50';
      case 'warning':
        return 'border-l-4 border-yellow-500 bg-yellow-50';
      case 'success':
        return 'border-l-4 border-green-500 bg-green-50';
      default:
        return 'border-l-4 border-blue-500 bg-blue-50';
    }
  };

  const filteredLogs = logs.filter(log => {
    if (filters.level && log.level?.toLowerCase() !== filters.level.toLowerCase()) {
      return false;
    }
    if (filters.search && !log.message?.toLowerCase().includes(filters.search.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div data-testid="logs-page">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Registros</h1>
          <p className="text-gray-600 mt-1">Ver historial de rastreo y registros del sistema</p>
        </div>

        <button
          onClick={fetchLogs}
          data-testid="refresh-logs-button"
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all"
          disabled={loading}
        >
          <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
          <span>Actualizar</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-lg p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              data-testid="log-search-input"
              placeholder="Search logs..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nivel
            </label>
            <select
              value={filters.level}
              onChange={(e) => setFilters(prev => ({ ...prev, level: e.target.value }))}
              data-testid="log-level-filter"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los niveles</option>
              <option value="info">Info</option>
              <option value="success">Success</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
            </select>
          </div>
        </div>
      </div>

      {/* Logs List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredLogs.length > 0 ? (
        <div className="space-y-3">
          {filteredLogs.map((log, index) => (
            <div
              key={log.id || index}
              data-testid="log-entry"
              className={`rounded-lg p-4 ${getLogColor(log.level)} transition-all hover:shadow-md`}
            >
              <div className="flex items-start space-x-3">
                <div className="mt-0.5">{getLogIcon(log.level)}</div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-gray-900 uppercase text-sm">
                      {log.level || 'INFO'}
                    </span>
                    <span className="text-sm text-gray-500">
                      {log.timestamp 
                        ? format(new Date(log.timestamp), 'MMM dd, yyyy HH:mm:ss')
                        : 'N/A'
                      }
                    </span>
                  </div>
                  <p className="text-gray-700">{log.message || 'No message'}</p>
                  {log.search_name && (
                    <p className="text-sm text-gray-600 mt-1">
                      Search: <span className="font-medium">{log.search_name}</span>
                    </p>
                  )}
                  {log.details && (
                    <details className="mt-2">
                      <summary className="text-sm text-blue-600 cursor-pointer hover:text-blue-800">
                        View Details
                      </summary>
                      <pre className="mt-2 text-xs bg-white/50 p-2 rounded overflow-x-auto">
                        {JSON.stringify(log.details, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20 bg-white rounded-xl shadow-lg">
          <div className="text-6xl mb-4">📄</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">No se encontraron registros</h3>
          <p className="text-gray-600">
            {filters.search || filters.level
              ? 'Intenta ajustar tus filtros'
              : 'Aún no hay registros disponibles. Inicia el rastreo para ver los registros aquí.'}
          </p>
        </div>
      )}
    </div>
  );
};

export default Logs;
