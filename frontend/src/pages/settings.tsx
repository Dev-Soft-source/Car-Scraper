import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";
import searchService from "@/services/search.service";
import settingsService from "@/services/settings.service";

type UrlItem = { id: string; url: string };
type SearchItem = { id: string; name: string; description?: string; site_url?: string };

export default function SettingsPage() {
  const [siteUrls, setSiteUrls] = useState<UrlItem[]>([]);
  const [newUrl, setNewUrl] = useState("");
  const [searches, setSearches] = useState<SearchItem[]>([]);
  const [passwords, setPasswords] = useState({ old: "", next: "", confirm: "" });

  const fetchData = async () => {
    try {
      const [urlsRes, searchesRes] = await Promise.all([settingsService.getSiteUrls(), searchService.getAllSearches()]);
      setSiteUrls(urlsRes.data as UrlItem[]);
      setSearches(searchesRes.data as SearchItem[]);
    } catch {
      toast.error("Error fetching settings data");
    }
  };

  useEffect(() => {
    // Initial data load from backend APIs.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void fetchData();
  }, []);

  const addUrl = async () => {
    if (!newUrl.trim()) return;
    try {
      await settingsService.addSiteUrl(newUrl);
      setNewUrl("");
      await fetchData();
      toast.success("URL added");
    } catch {
      toast.error("Could not add URL");
    }
  };

  const removeUrl = async (id: string) => {
    try {
      await settingsService.deleteSiteUrl(id);
      await fetchData();
      toast.success("URL deleted");
    } catch {
      toast.error("Could not delete URL");
    }
  };

  const changePassword = async () => {
    if (passwords.next !== passwords.confirm) {
      toast.error("Passwords do not match");
      return;
    }
    try {
      await settingsService.changePassword(passwords.old, passwords.next);
      setPasswords({ old: "", next: "", confirm: "" });
      toast.success("Password updated");
    } catch {
      toast.error("Could not update password");
    }
  };

  return (
    <ProtectedRoute>
      <Layout>
        <div>
          <h1 className="mb-6 text-3xl font-bold text-gray-900">Configuracion</h1>
          <div className="mb-6 rounded-xl bg-white p-6 shadow-lg">
            <h2 className="mb-4 text-xl font-bold">Site URLs</h2>
            <div className="mb-4 flex gap-2">
              <input
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                placeholder="https://example.com"
                className="flex-1 rounded border px-4 py-2"
              />
              <button onClick={() => void addUrl()} className="rounded bg-blue-600 px-4 py-2 text-white">
                Add
              </button>
            </div>
            <div className="space-y-2">
              {siteUrls.map((url) => (
                <div key={url.id} className="flex items-center justify-between rounded bg-gray-50 p-3">
                  <span>{url.url}</span>
                  <button onClick={() => void removeUrl(url.id)} className="rounded bg-red-100 px-2 py-1 text-red-700">
                    Delete
                  </button>
                </div>
              ))}
            </div>
          </div>
          <div className="mb-6 rounded-xl bg-white p-6 shadow-lg">
            <h2 className="mb-4 text-xl font-bold">Saved Searches</h2>
            <div className="space-y-2">
              {searches.map((search) => (
                <div key={search.id} className="rounded bg-slate-50 p-3">
                  <div className="font-medium">{search.name}</div>
                  <div className="text-sm text-gray-600">{search.description}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-xl bg-white p-6 shadow-lg">
            <h2 className="mb-4 text-xl font-bold">Change Password</h2>
            <div className="max-w-md space-y-3">
              <input
                type="password"
                value={passwords.old}
                onChange={(e) => setPasswords((p) => ({ ...p, old: e.target.value }))}
                placeholder="Current password"
                className="w-full rounded border px-4 py-2"
              />
              <input
                type="password"
                value={passwords.next}
                onChange={(e) => setPasswords((p) => ({ ...p, next: e.target.value }))}
                placeholder="New password"
                className="w-full rounded border px-4 py-2"
              />
              <input
                type="password"
                value={passwords.confirm}
                onChange={(e) => setPasswords((p) => ({ ...p, confirm: e.target.value }))}
                placeholder="Confirm new password"
                className="w-full rounded border px-4 py-2"
              />
              <button onClick={() => void changePassword()} className="rounded bg-indigo-600 px-4 py-2 text-white">
                Save password
              </button>
            </div>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
}
