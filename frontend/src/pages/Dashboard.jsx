import { useState, useEffect, useCallback } from "react";
import UploadZone from "../components/UploadZone";
import TranscriptionCard from "../components/TranscriptionCard";
import { api } from "../api/client";
import { RefreshCw } from "lucide-react";

const POLL_INTERVAL = 5000; // 5 secondes

export default function Dashboard() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchRecent = useCallback(async () => {
    try {
      const res = await api.list({ page: 1, perPage: 10 });
      setItems(res.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Polling automatique si des jobs sont en cours
  useEffect(() => {
    fetchRecent();
    const hasActive = items.some(
      (i) => i.status === "pending" || i.status === "processing"
    );
    if (!hasActive) return;
    const timer = setInterval(fetchRecent, POLL_INTERVAL);
    return () => clearInterval(timer);
  }, [fetchRecent, items.map((i) => i.status).join(",")]);

  const handleUploaded = (newItem) => {
    setItems((prev) => [newItem, ...prev]);
    // Refresh immédiat pour récupérer les statuts
    setTimeout(fetchRecent, 1000);
  };

  const handleDelete = (id) => {
    setItems((prev) => prev.filter((i) => i.id !== id));
  };

  const activeCount = items.filter(
    (i) => i.status === "pending" || i.status === "processing"
  ).length;

  return (
    <div className="space-y-8">
      {/* Upload */}
      <div>
        <h1 className="text-xl font-semibold text-gray-900 mb-1">Nouvelle transcription</h1>
        <p className="text-sm text-gray-500 mb-4">
          Déposez vos fichiers audio. Ils seront transcrits automatiquement en arrière-plan.
        </p>
        <UploadZone onUploaded={handleUploaded} />
      </div>

      {/* Activité récente */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-gray-900">Activité récente</h2>
            {activeCount > 0 && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-sky-100 text-sky-700 text-xs rounded-full font-medium">
                {activeCount} en cours
              </span>
            )}
          </div>
          <button
            onClick={fetchRecent}
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700"
          >
            <RefreshCw className="w-4 h-4" />
            Actualiser
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400 text-sm">Chargement...</div>
        ) : items.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <p className="text-sm">Aucune transcription pour l'instant.</p>
            <p className="text-xs mt-1">Déposez un fichier audio ci-dessus pour commencer.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {items.map((item) => (
              <TranscriptionCard
                key={item.id}
                transcription={item}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
