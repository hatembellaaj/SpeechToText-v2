import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileAudio, X, Loader2 } from "lucide-react";
import { api } from "../api/client";

const ACCEPTED = {
  "audio/*": [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".webm"],
  "video/*": [".mp4"],
};

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1024 / 1024).toFixed(1) + " MB";
}

function FileRow({ file, onRemove }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
      <FileAudio className="w-5 h-5 text-sky-500 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-800 truncate">{file.name}</p>
        <p className="text-xs text-gray-400">{formatBytes(file.size)}</p>
      </div>
      {file.status === "uploading" && (
        <div className="w-24 bg-gray-200 rounded-full h-1.5">
          <div
            className="bg-sky-500 h-1.5 rounded-full transition-all"
            style={{ width: `${file.progress}%` }}
          />
        </div>
      )}
      {file.status === "done" && (
        <span className="text-xs text-green-600 font-medium">✓ Envoyé</span>
      )}
      {file.status === "error" && (
        <span className="text-xs text-red-500 font-medium" title={file.error}>✗ Erreur</span>
      )}
      {file.status === "pending" && (
        <button onClick={() => onRemove(file.id)} className="text-gray-400 hover:text-gray-600">
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}

export default function UploadZone({ onUploaded }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((accepted) => {
    const newFiles = accepted.map((f) => ({
      id: Math.random().toString(36).slice(2),
      file: f,
      name: f.name,
      size: f.size,
      status: "pending",
      progress: 0,
      error: null,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    maxSize: 500 * 1024 * 1024,
  });

  const removeFile = (id) => setFiles((prev) => prev.filter((f) => f.id !== id));

  const uploadAll = async () => {
    const pending = files.filter((f) => f.status === "pending");
    if (!pending.length) return;
    setUploading(true);

    for (const item of pending) {
      setFiles((prev) =>
        prev.map((f) => (f.id === item.id ? { ...f, status: "uploading" } : f))
      );
      try {
        const result = await api.upload(item.file, (progress) => {
          setFiles((prev) =>
            prev.map((f) => (f.id === item.id ? { ...f, progress } : f))
          );
        });
        setFiles((prev) =>
          prev.map((f) => (f.id === item.id ? { ...f, status: "done" } : f))
        );
        onUploaded?.(result);
      } catch (err) {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === item.id ? { ...f, status: "error", error: err.message } : f
          )
        );
      }
    }
    setUploading(false);
  };

  const pendingCount = files.filter((f) => f.status === "pending").length;

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-sky-400 bg-sky-50"
            : "border-gray-300 hover:border-sky-400 hover:bg-sky-50/50"
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-700 font-medium">
          {isDragActive ? "Déposez ici..." : "Glissez vos fichiers audio ici"}
        </p>
        <p className="text-sm text-gray-400 mt-1">
          ou <span className="text-sky-600 underline">parcourez</span> — MP3, WAV, M4A, FLAC, OGG, MP4 (max 500 MB)
        </p>
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((f) => (
            <FileRow key={f.id} file={f} onRemove={removeFile} />
          ))}

          {pendingCount > 0 && (
            <button
              onClick={uploadAll}
              disabled={uploading}
              className="w-full py-2.5 bg-sky-600 hover:bg-sky-700 disabled:bg-sky-300 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {uploading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Envoi en cours...</>
              ) : (
                <><Upload className="w-4 h-4" /> Transcrire {pendingCount} fichier{pendingCount > 1 ? "s" : ""}</>
              )}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
