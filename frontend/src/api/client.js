const BASE_URL = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur réseau");
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Upload
  upload(file, onProgress) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append("file", file);

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable && onProgress) {
          onProgress(Math.round((e.loaded / e.total) * 100));
        }
      };

      xhr.onload = () => {
        if (xhr.status === 202) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          const err = JSON.parse(xhr.responseText || "{}");
          reject(new Error(err.detail || "Erreur upload"));
        }
      };

      xhr.onerror = () => reject(new Error("Erreur réseau"));

      xhr.open("POST", `${BASE_URL}/transcriptions/upload`);
      xhr.send(formData);
    });
  },

  // Liste
  list({ page = 1, perPage = 20, status, search } = {}) {
    const params = new URLSearchParams({ page, per_page: perPage });
    if (status) params.set("status", status);
    if (search) params.set("search", search);
    return request(`/transcriptions?${params}`);
  },

  // Détail
  get(id) {
    return request(`/transcriptions/${id}`);
  },

  // Supprimer
  delete(id) {
    return request(`/transcriptions/${id}`, { method: "DELETE" });
  },

  // Télécharger texte brut
  downloadText(id, filename) {
    const link = document.createElement("a");
    link.href = `${BASE_URL}/transcriptions/${id}/text`;
    link.download = filename.replace(/\.[^.]+$/, ".txt");
    link.click();
  },
};

// ── PROFILER API ──────────────────────────────────────────────────────────────

export const projectsApi = {
  list: () => request("/projects"),
  get: (id) => request(`/projects/${id}`),
  create: (data) => request("/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }),
  delete: (id) => request(`/projects/${id}`, { method: "DELETE" }),
  stats: (projectId, batchId) => {
    const params = batchId ? `?batch_id=${batchId}` : "";
    return request(`/projects/${projectId}/stats${params}`);
  },
  createBatch: (projectId, data) => request(`/projects/${projectId}/batches`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }),
  listBatches: (projectId) => request(`/projects/${projectId}/batches`),
};

export const analysisApi = {
  trigger: (transcriptionId, projectId) => request("/analysis", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transcription_id: transcriptionId, project_id: projectId }),
  }),
  getForTranscription: (transcriptionId) =>
    request(`/analysis/transcription/${transcriptionId}`),
  get: (id) => request(`/analysis/${id}`),
};
