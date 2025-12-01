import React from 'react';
import { Search, X, Filter } from 'lucide-react';

const FilterPanel = ({ filters, setFilters, onClear }) => {
  const handleChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="bg-[#e4f5f5] rounded-xl shadow-lg p-6 mb-6" data-testid="filter-panel">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Filter className="text-blue-600" size={20} />
          <h2 className="text-xl font-bold text-gray-900">Filtros</h2>
        </div>
        <button
          onClick={onClear}
          data-testid="clear-filters-button"
          className="flex items-center space-x-1 text-sm text-gray-600 hover:text-red-600 transition-colors"
        >
          <X size={16} />
          <span>Borrar todo</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Buscar
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              value={filters.search || ''}
              onChange={(e) => handleChange('search', e.target.value)}
              data-testid="search-input"
              placeholder="Buscar listados..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Make */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Marca
          </label>
          <input
            type="text"
            value={filters.make || ''}
            onChange={(e) => handleChange('make', e.target.value)}
            data-testid="make-input"
            placeholder="e.g., BMW, Audi"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Model */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Modelo
          </label>
          <input
            type="text"
            value={filters.model || ''}
            onChange={(e) => handleChange('model', e.target.value)}
            data-testid="model-input"
            placeholder="e.g., X5, A4"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ubicación
          </label>
          <input
            type="text"
            value={filters.location || ''}
            onChange={(e) => handleChange('location', e.target.value)}
            data-testid="location-input"
            placeholder="Ciudad o región"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Min Price */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Precio mínimo (€)
          </label>
          <input
            type="number"
            value={filters.min_price || ''}
            onChange={(e) => handleChange('min_price', e.target.value)}
            data-testid="min-price-input"
            placeholder="0"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Max Price */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Precio máximo (€)
          </label>
          <input
            type="number"
            value={filters.max_price || ''}
            onChange={(e) => handleChange('max_price', e.target.value)}
            data-testid="max-price-input"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Seller Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de vendedor
          </label>
          <select
            value={filters.seller_type || ''}
            onChange={(e) => handleChange('seller_type', e.target.value)}
            data-testid="seller-type-select"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Toda</option>
            <option value="Private">Particular</option>
            <option value="Professional">Profesional</option>
          </select>
        </div>

        {/* Target Price Only */}
        <div className="flex items-end">
          <label className="flex items-center space-x-2 cursor-pointer mb-4">
            <input
              type="checkbox"
              checked={filters.target_price_only || false}
              onChange={(e) => handleChange('target_price_only', e.target.checked)}
              data-testid="target-price-checkbox"
              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm font-medium text-gray-700">Solo por debajo del precio objetivo</span>
          </label>
        </div>
      </div>

      {/* Sort */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Ordenar por
        </label>
        <div className="flex space-x-2">
          {[
            { value: 'price_asc', label: 'Precio: bajo a alto' },
            { value: 'price_desc', label: 'Precio: Alto a bajo' },
            { value: 'date_desc', label: 'Lo más nuevo primero' },
            { value: 'date_asc', label: 'Más antiguo primero' },
          ].map((option) => (
            <button
              key={option.value}
              onClick={() => handleChange('sort', option.value)}
              data-testid={`sort-${option.value}`}
              className={`px-4 py-2 rounded-lg bg-[#dcdcdc] hover:bg-[#afaeae] text-sm font-medium transition-all ${
                filters.sort === option.value
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FilterPanel;
