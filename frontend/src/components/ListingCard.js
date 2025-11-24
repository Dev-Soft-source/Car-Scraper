import React from 'react';
import { Heart, ExternalLink, MapPin, Calendar, Fuel, Gauge } from 'lucide-react';
import { format } from 'date-fns';

const ListingCard = ({ listing, onToggleFavorite }) => {
  const isBelowTarget = listing.target_price_met;
  const isProfessional = listing.seller_type === 'Professional';

  return (
    <div 
      data-testid="listing-card"
      className={`bg-white rounded-xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 ${
        isBelowTarget ? 'ring-2 ring-green-500 ring-offset-2' : ''
      }`}
    >
      {/* Image */}
      <div className="relative h-48 bg-gradient-to-br from-blue-100 to-purple-100">
        {listing.image_url ? (
          <img 
            src={listing.image_url} 
            alt={listing.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <span className="text-4xl">📦</span>
          </div>
        )}
        
        {/* Favorite Button */}
        <button
          onClick={() => onToggleFavorite(listing.id)}
          data-testid="favorite-button"
          className="absolute top-3 right-3 p-2 bg-white/90 rounded-full hover:bg-white transition-all"
        >
          <Heart 
            size={20} 
            className={listing.is_favorite ? 'fill-red-500 text-red-500' : 'text-gray-600'}
          />
        </button>

        {/* Target Price Badge */}
        {isBelowTarget && (
          <div className="absolute top-3 left-3 px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full animate-pulse">
            Below Target 🎯
          </div>
        )}

        {/* Professional Badge */}
        {isProfessional && (
          <div className="absolute bottom-3 left-3 px-2 py-1 bg-blue-500 text-white text-xs rounded-full">
            Professional
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-5">
        {/* Title */}
        <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2" data-testid="listing-title">
          {listing.title || listing.description}
        </h3>

        {/* Vehicle Details */}
        <div className="grid grid-cols-2 gap-2 mb-3 text-sm">
          {listing.make && (
            <div className="flex items-center text-gray-600">
              <span className="font-semibold">Make:</span>
              <span className="ml-1">{listing.make}</span>
            </div>
          )}
          {listing.model && (
            <div className="flex items-center text-gray-600">
              <span className="font-semibold">Model:</span>
              <span className="ml-1">{listing.model}</span>
            </div>
          )}
          {listing.year && (
            <div className="flex items-center text-gray-600">
              <Calendar size={14} className="mr-1" />
              <span>{listing.year}</span>
            </div>
          )}
          {listing.mileage && (
            <div className="flex items-center text-gray-600">
              <Gauge size={14} className="mr-1" />
              <span>{listing.mileage.toLocaleString()} km</span>
            </div>
          )}
          {listing.fuel_type && (
            <div className="flex items-center text-gray-600">
              <Fuel size={14} className="mr-1" />
              <span>{listing.fuel_type}</span>
            </div>
          )}
          {listing.location && (
            <div className="flex items-center text-gray-600">
              <MapPin size={14} className="mr-1" />
              <span className="truncate">{listing.location}</span>
            </div>
          )}
        </div>

        {/* Price Section */}
        <div className="flex items-center justify-between mb-3 pt-3 border-t border-gray-200">
          <div>
            <div className="text-2xl font-bold text-blue-600" data-testid="listing-price">
              €{listing.price?.toLocaleString() || 'N/A'}
            </div>
            {listing.average_price && (
              <div className="text-xs text-gray-500">
                Avg: €{listing.average_price.toLocaleString()}
              </div>
            )}
          </div>
          
          {listing.platform_url && (
            <a
              href={listing.platform_url}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="view-listing-button"
              className="flex items-center space-x-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
            >
              <span className="text-sm font-medium">View</span>
              <ExternalLink size={14} />
            </a>
          )}
        </div>

        {/* Last Updated */}
        {listing.last_updated && (
          <div className="text-xs text-gray-400">
            Updated: {format(new Date(listing.last_updated), 'MMM dd, yyyy HH:mm')}
          </div>
        )}
      </div>
    </div>
  );
};

export default ListingCard;
