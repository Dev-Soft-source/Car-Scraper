import { useEffect, useMemo, useState } from "react";
import { format } from "date-fns";
import { toast } from "react-toastify";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";
import logsService from "@/services/logs.service";

type LogItem = {
  id?: string;
  level?: string;
  message?: string;
  timestamp?: string;
  details?: unknown;
};

export default function LogsPage() {
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [level, setLevel] = useState("");
  const [search, setSearch] = useState("");

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await logsService.getAllLogs({ level, search });
      setLogs(response.data as LogItem[]);
    } catch {
      toast.error("Error fetching logs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filtered = useMemo(
    () =>
      logs.filter((log) => {
        if (level && (log.level || "").toLowerCase() !== level.toLowerCase()) return false;
        if (search && !(log.message || "").toLowerCase().includes(search.toLowerCase())) return false;
        return true;
      }),
    [logs, level, search],
  );

  return (
    <ProtectedRoute>
      <Layout>
        <div>
          <h1 className="mb-4 text-3xl font-bold text-gray-900">Registros</h1>
          <div className="mb-4 grid grid-cols-1 gap-3 rounded-xl bg-white p-4 shadow md:grid-cols-3">
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search log message"
              className="rounded border px-3 py-2"
            />
            <select value={level} onChange={(e) => setLevel(e.target.value)} className="rounded border px-3 py-2">
              <option value="">All levels</option>
              <option value="info">Info</option>
              <option value="success">Success</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
            </select>
            <button onClick={() => void fetchLogs()} className="rounded bg-blue-600 px-3 py-2 text-white">
              Refresh
            </button>
          </div>
          {loading ? (
            <div>Loading...</div>
          ) : (
            <div className="space-y-2">
              {filtered.map((log, i) => (
                <div key={log.id || i} className="rounded border-l-4 border-blue-500 bg-white p-4 shadow">
                  <div className="mb-1 flex justify-between text-sm text-gray-500">
                    <span className="uppercase">{log.level || "info"}</span>
                    <span>{log.timestamp ? format(new Date(log.timestamp), "MMM dd, yyyy HH:mm:ss") : "N/A"}</span>
                  </div>
                  <p className="text-gray-800">{log.message || "No message"}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </Layout>
    </ProtectedRoute>
  );
}
