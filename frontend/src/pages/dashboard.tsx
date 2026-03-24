import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";
import listingService from "@/services/listing.service";
import searchService from "@/services/search.service";

type Listing = {
  id: string;
  title?: string;
  description?: string;
  price?: number;
  target_price_met?: boolean;
  is_favorite?: boolean;
};

type SearchItem = {
  id: string;
  name: string;
  description?: string;
  site_url?: string;
};

export default function DashboardPage() {
  const [searches, setSearches] = useState<SearchItem[]>([]);
  const [activeSearch, setActiveSearch] = useState("");
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchSearches = async () => {
    try {
      const response = await searchService.getAllSearches();
      const data = response.data as SearchItem[];
      setSearches(data);
      if (data.length > 0 && !activeSearch) setActiveSearch(data[0].id);
    } catch {
      toast.error("Error fetching searches");
    }
  };

  const fetchListings = async () => {
    if (!activeSearch) return;
    setLoading(true);
    try {
      const response = await listingService.getListingsBySearch(activeSearch);
      setListings(response.data as Listing[]);
    } catch {
      toast.error("Error fetching listings");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (listingId: string) => {
    try {
      await listingService.toggleFavorite(listingId);
      setListings((prev) => prev.map((l) => (l.id === listingId ? { ...l, is_favorite: !l.is_favorite } : l)));
    } catch {
      toast.error("Error updating favorite");
    }
  };

  useEffect(() => {
    void fetchSearches();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    void fetchListings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSearch]);

  return (
    <ProtectedRoute>
      <Layout>
        <div>
          <h1 className="mb-4 text-3xl font-bold text-gray-900">Panel</h1>
          <div className="mb-6 rounded-xl bg-white p-4 shadow">
            <label className="mb-2 block text-sm text-gray-700">Busqueda activa</label>
            <select
              value={activeSearch}
              onChange={(e) => setActiveSearch(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
            >
              {searches.map((search) => (
                <option key={search.id} value={search.id}>
                  {search.name} ({search.site_url}) - {search.description}
                </option>
              ))}
            </select>
          </div>
          <button onClick={() => void fetchListings()} className="mb-6 rounded bg-blue-600 px-4 py-2 text-white">
            Refresh
          </button>
          {loading ? (
            <div className="py-10">Loading...</div>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {listings.map((listing) => (
                <div key={listing.id} className="rounded-lg border bg-white p-4 shadow-sm">
                  <h3 className="font-semibold">{listing.title || listing.description || "Listing"}</h3>
                  <p className="text-sm text-gray-600">Price: EUR {listing.price ?? "N/A"}</p>
                  <div className="mt-3 flex gap-2">
                    {listing.target_price_met && (
                      <span className="rounded bg-green-100 px-2 py-1 text-xs text-green-700">Below target</span>
                    )}
                    <button
                      onClick={() => void handleToggleFavorite(listing.id)}
                      className="rounded bg-purple-100 px-2 py-1 text-xs text-purple-700"
                    >
                      {listing.is_favorite ? "Unfavorite" : "Favorite"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Layout>
    </ProtectedRoute>
  );
}
