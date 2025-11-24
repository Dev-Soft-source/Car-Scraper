import React from 'react';
import { BarChart, Bar, LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ListingCharts = ({ listings }) => {
  // Prepare price distribution data
  const priceRanges = [
    { range: '0-5k', min: 0, max: 5000 },
    { range: '5k-10k', min: 5000, max: 10000 },
    { range: '10k-20k', min: 10000, max: 20000 },
    { range: '20k-30k', min: 20000, max: 30000 },
    { range: '30k+', min: 30000, max: Infinity },
  ];

  const priceDistribution = priceRanges.map(range => ({
    range: range.range,
    count: listings.filter(l => l.price >= range.min && l.price < range.max).length,
  }));

  // Prepare year vs price data
  const yearPriceData = listings
    .filter(l => l.year && l.price)
    .reduce((acc, listing) => {
      const existing = acc.find(item => item.year === listing.year);
      if (existing) {
        existing.total += listing.price;
        existing.count += 1;
        existing.avgPrice = existing.total / existing.count;
      } else {
        acc.push({
          year: listing.year,
          total: listing.price,
          count: 1,
          avgPrice: listing.price,
        });
      }
      return acc;
    }, [])
    .sort((a, b) => a.year - b.year);

  // Prepare mileage vs price scatter data
  const mileagePriceData = listings
    .filter(l => l.mileage && l.price)
    .map(l => ({
      mileage: l.mileage,
      price: l.price,
    }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      {/* Price Distribution */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Price Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={priceDistribution}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="range" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#3b82f6" name="Number of Listings" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Year vs Average Price */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Average Price by Year</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={yearPriceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip formatter={(value) => `€${value.toLocaleString()}`} />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="avgPrice" 
              stroke="#8b5cf6" 
              strokeWidth={2}
              name="Avg Price"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Mileage vs Price Scatter */}
      <div className="bg-white rounded-xl shadow-lg p-6 lg:col-span-2">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Mileage vs Price Correlation</h3>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="mileage" 
              name="Mileage" 
              unit=" km"
              type="number"
            />
            <YAxis 
              dataKey="price" 
              name="Price" 
              unit="€"
              type="number"
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              formatter={(value, name) => [
                name === 'price' ? `€${value.toLocaleString()}` : `${value.toLocaleString()} km`,
                name === 'price' ? 'Price' : 'Mileage'
              ]}
            />
            <Legend />
            <Scatter 
              name="Listings" 
              data={mileagePriceData} 
              fill="#10b981"
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ListingCharts;
