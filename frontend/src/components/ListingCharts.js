import React from "react";
import { useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const ListingCharts = ({ listings }) => {
  const [minyear, setMinYear] = useState("");
  const [maxyear, setMaxYear] = useState("");

  // -----------------------------
  // PRICE DISTRIBUTION RANGES
  // -----------------------------
  const priceRanges = [
    { range: "0-5k", min: 0, max: 5000 },
    { range: "5k-10k", min: 5000, max: 10000 },
    { range: "10k-15k", min: 10001, max: 15000 },
    { range: "15k-20k", min: 15001, max: 20000 },
    { range: "20k-30k", min: 20001, max: 30000 },
    { range: "30k+", min: 30000, max: Infinity },
  ];

  const priceDistribution = priceRanges.map((r) => ({
    range: r.range,
    count: listings.filter((l) => l.price >= r.min && l.price < r.max).length,
  }));

  // -----------------------------
  // AVERAGE PRICE PER YEAR
  // -----------------------------
  const yearPriceData = listings
    .filter((l) => l.year && l.price)
    .reduce((acc, listing) => {
      const found = acc.find((y) => y.year === listing.year);
      if (found) {
        found.total += listing.price;
        found.count += 1;
        found.avgPrice = found.total / found.count;
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

  // -----------------------------
  // MILAGE CATEGORY HELPER
  // -----------------------------
  const getMileageCategory = (km) => {
    if (km <= 50000) return "K1";
    if (km > 50001 && km <= 100000) return "K2";
    if (km > 100001 && km <= 150000) return "K3";
    if (km > 150001 && km <= 200000) return "K4";
    if (km > 200001 && km <= 300000) return "K5";
    if (km > 300001) return "K6";
  };

  // -----------------------------
  // AUTO-BUILD mileageData
  // -----------------------------
  const mileageData = {
    K1: [],
    K2: [],
    K3: [],
    K4: [],
    K5: [],
    K6: [],
  };

  listings.forEach((l) => {
    if (!l.year || !l.price || !l.mileage) return;
  
    // Update min and max year
    if (l.year < minyear) setMinYear(l.year);
    if (l.year > maxyear) setMaxYear(l.year);
  
    const cat = getMileageCategory(l.mileage);
    mileageData[cat].push({
      year: l.year,
      price: l.price,
      mileage: l.mileage,
    });
  });

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="bg-white p-2 rounded shadow text-sm">
          <div><strong>Year:</strong> {d.year}</div>
          <div><strong>Price:</strong> €{d.price.toLocaleString()}</div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      {/* ------------------------------
          PRICE DISTRIBUTION BAR CHART
      ------------------------------- */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Price Distribution</h3>

        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={priceDistribution}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="range" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#3b82f6" name="Listings" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ------------------------------
          AVG PRICE BY YEAR LINE CHART
      ------------------------------- */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Average Price by Year</h3>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={yearPriceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip formatter={(v) => `€${v.toLocaleString()}`} />
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

      {/* ------------------------------
          MILEAGE CATEGORY SCATTER CHART
      ------------------------------- */}
      <div className="bg-white rounded-xl shadow-lg p-6 lg:col-span-2">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          RENAULT CLIO - COCHES USADOS
        </h3>

        <ResponsiveContainer width="100%" height={350}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />

            {/* X = Year */}
            <XAxis
              type="number"
              dataKey="year"
              name="Year"
              domain={[minyear, maxyear]}
              tickFormatter={(v) => v.toString()}
            />

            {/* Y = Price */}
            <YAxis type="number" dataKey="price" unit="€" name="Price" />

            {/* <Tooltip content={<CustomTooltip />} /> */}
            <Legend />

            {/* CATEGORY SCATTERS */}
            <Scatter name="K1 (0–50k km)" data={mileageData.K1} fill="#A7F3D0" shape="x" />
            <Scatter name="K2 (50–100k km)" data={mileageData.K2} fill="#047857" shape="circle" />
            <Scatter name="K3 (100–150k km)" data={mileageData.K3} fill="#FDE68A" shape="square" />
            <Scatter name="K4 (150–200k km)" data={mileageData.K4} fill="#CA8A04" shape="triangle" />
            <Scatter name="K5 (200–300k km)" data={mileageData.K5} fill="#FCA5A5" shape="diamond" />
            <Scatter name="K6 (>300k km)" data={mileageData.K6} fill="#B91C1C" shape="cross" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ListingCharts;
