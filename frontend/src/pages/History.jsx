import { useState, useEffect, useCallback } from "react";
import TranscriptionCard from "../components/TranscriptionCard";
import { api } from "../api/client";
import { Search, Filter, ChevronLeft, ChevronRight } from "lucide-react";

const STATUSES = [
  { value: "", label: "Tous" },
  { value: "completed", label: "Terminés" },
  { value: "processing", label: "En cours" },
  { value: "pending", label: "En attente" },
  { value: "failed", label: "Échecs" },
];

export default function History() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const PER_PAGE = 20;

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.list({
        page,
        perPage: PER_PAGE,
        status: statusFilter || undefined,
        search: search || undefined,
      });
      setItems(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, search, statusFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Reset page si filtres changent
  useEffect(() => {
    setPage(1);
  }, [search, statusFilter]);

  const handleDelete = (id) => {
    setItems((prev) => prev.filter((i) => i.id !== id));
    setTotal((t) => t - 1);
  };

  const totalPages = Math.ceil(total / PER_PAGE);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-gray-900 mb-1">Historique</h1>
        <p className="text-sm text-gray-500">{total} transcription{total > 1 ? "s" : ""} au total</p>
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher par nom de fichier ou contenu..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="pl-9 pr-8 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 appearance-none bg-white"
          >
            {STATUSES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Liste */}
      {loading ? (
        <div className="text-center py-12 text-gray-400 text-sm">Chargement...</div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-sm">Aucun résultat{search ? ` pour "${search}"` : ""}.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <TranscriptionCard key={item.id} transcription={item} onDelete={handleDelete} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <p className="text-sm text-gray-500">
            Page {page} sur {totalPages}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="flex items-center gap-1 px-3 py-1.5 text-sm border border-gray-200 rounded-lg disabled:opacity-40 hover:bg-gray-50 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" /> Précédent
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="flex items-center gap-1 px-3 py-1.5 text-sm border border-gray-200 rounded-lg disabled:opacity-40 hover:bg-gray-50 transition-colors"
            >
              Suivant <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
