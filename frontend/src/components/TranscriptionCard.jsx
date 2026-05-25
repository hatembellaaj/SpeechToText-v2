import { useState } from "react";
import { Copy, Download, Trash2, ChevronDown, ChevronUp, Clock, FileAudio } from "lucide-react";
import StatusBadge from "./StatusBadge";
import { api } from "../api/client";

function formatDuration(seconds) {
  if (!seconds) return "—";
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

function formatDate(iso) {
  return new Date(iso).toLocaleString("fr-FR", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

function formatBytes(bytes) {
  if (!bytes) return "—";
  return (bytes / 1024 / 1024).toFixed(1) + " MB";
}

export default function TranscriptionCard({ transcription, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const { id, original_filename, status, text, duration_seconds,
          processing_time_seconds, created_at, file_size_bytes } = transcription;

  const handleCopy = () => {
    navigator.clipboard.writeText(text || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDelete = async () => {
    if (!confirm(`Supprimer "${original_filename}" ?`)) return;
    await api.delete(id);
    onDelete?.(id);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 p-4">
        <FileAudio className="w-5 h-5 text-sky-500 shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 truncate">{original_filename}</p>
          <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatDate(created_at)}
            </span>
            {duration_seconds && <span>Durée : {formatDuration(duration_seconds)}</span>}
            {file_size_bytes && <span>{formatBytes(file_size_bytes)}</span>}
            {processing_time_seconds && (
              <span>Traitement : {formatDuration(processing_time_seconds)}</span>
            )}
          </div>
        </div>
        <StatusBadge status={status} />
      </div>

      {/* Texte */}
      {status === "completed" && text && (
        <>
          <div className={`px-4 pb-2 overflow-hidden transition-all ${expanded ? "" : "max-h-24"}`}>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{text}</p>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 px-4 pb-4">
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
            >
              {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              {expanded ? "Réduire" : "Voir tout"}
            </button>
            <div className="flex-1" />
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Copy className="w-3.5 h-3.5" />
              {copied ? "Copié !" : "Copier"}
            </button>
            <button
              onClick={() => api.downloadText(id, original_filename)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              .txt
            </button>
            <button
              onClick={handleDelete}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs border border-red-100 text-red-500 rounded-lg hover:bg-red-50 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Supprimer
            </button>
          </div>
        </>
      )}

      {status === "failed" && transcription.error_message && (
        <div className="px-4 pb-4">
          <p className="text-sm text-red-600 bg-red-50 rounded-lg p-3">
            {transcription.error_message}
          </p>
          <div className="flex justify-end mt-2">
            <button onClick={handleDelete} className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-red-500 hover:text-red-700">
              <Trash2 className="w-3.5 h-3.5" /> Supprimer
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
