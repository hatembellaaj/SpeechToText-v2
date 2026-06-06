import { useState, useEffect } from "react";
import { Brain, ChevronDown, ChevronUp, Star, Tag, RefreshCw } from "lucide-react";
import { analysisApi, projectsApi } from "../api/client";

const SENTIMENT_ICON = { "+": "😊", "neutre": "😐", "-": "😞" };
const SENTIMENT_COLOR = {
  "+": "text-emerald-600 bg-emerald-50 border-emerald-200",
  "neutre": "text-gray-500 bg-gray-50 border-gray-200",
  "-": "text-red-600 bg-red-50 border-red-200",
};

function ProfileBadge({ name, color, confidence }) {
  return (
    <span
      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold border"
      style={{
        backgroundColor: color + "20",
        borderColor: color + "60",
        color: color,
      }}
    >
      <Brain className="w-3.5 h-3.5" />
      {name}
      {confidence && (
        <span className="text-xs opacity-70 font-normal">
          {Math.round(confidence * 100)}%
        </span>
      )}
    </span>
  );
}

function SatisfactionScore({ score }) {
  const color = score >= 7 ? "#10B981" : score >= 4 ? "#F59E0B" : "#EF4444";
  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
          <div
            key={i}
            className="w-2.5 h-5 rounded-sm"
            style={{ backgroundColor: i <= score ? color : "#E5E7EB" }}
          />
        ))}
      </div>
      <span className="text-sm font-semibold" style={{ color }}>
        {score}/10
      </span>
    </div>
  );
}

export default function AnalysisPanel({ transcriptionId, transcriptionStatus }) {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [showClusters, setShowClusters] = useState(false);

  useEffect(() => {
    projectsApi.list().then(setProjects).catch(() => {});
    // Charger analyse existante
    analysisApi.getForTranscription(transcriptionId)
      .then((list) => { if (list?.length > 0) setAnalysis(list[0]); })
      .catch(() => {});
  }, [transcriptionId]);

  const handleAnalyze = async () => {
    if (!selectedProject) return;
    setLoading(true);
    try {
      const a = await analysisApi.trigger(transcriptionId, selectedProject);
      setAnalysis(a);
      // Polling jusqu'à completion
      const poll = setInterval(async () => {
        const updated = await analysisApi.get(a.id);
        setAnalysis(updated);
        if (updated.status === "completed" || updated.status === "failed") {
          clearInterval(poll);
          setLoading(false);
        }
      }, 2000);
    } catch (e) {
      setLoading(false);
    }
  };

  if (transcriptionStatus !== "completed") return null;

  return (
    <div className="border-t border-gray-100 px-4 py-3">
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <Brain className="w-4 h-4 text-violet-500" />
        <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
          Analyse PROFILER
        </span>
      </div>

      {/* Résultat existant */}
      {analysis?.status === "completed" && (
        <div className="space-y-3">
          {/* Profil */}
          {analysis.profile_name && (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs text-gray-400">Profil :</span>
              <ProfileBadge
                name={analysis.profile_name}
                color={analysis.profile_color || "#7C3AED"}
                confidence={analysis.profile_confidence}
              />
            </div>
          )}

          {/* Score satisfaction */}
          {analysis.satisfaction_score != null && (
            <div className="flex items-center gap-2">
              <Star className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-xs text-gray-400">Satisfaction :</span>
              <SatisfactionScore score={Math.round(analysis.satisfaction_score)} />
            </div>
          )}

          {/* Reasoning profil */}
          {analysis.profile_reasoning && (
            <p className="text-xs text-gray-500 italic leading-relaxed">
              {analysis.profile_reasoning}
            </p>
          )}

          {/* Clusters toggle */}
          {analysis.clusters?.length > 0 && (
            <div>
              <button
                onClick={() => setShowClusters(!showClusters)}
                className="flex items-center gap-1 text-xs text-violet-600 hover:text-violet-800"
              >
                <Tag className="w-3 h-3" />
                {showClusters ? "Masquer" : "Voir"} les thèmes ({analysis.clusters.length})
                {showClusters ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>

              {showClusters && (
                <div className="mt-2 space-y-2">
                  {analysis.clusters.map((cluster, i) => (
                    <div key={i} className="rounded-lg border border-gray-100 p-2">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-semibold text-gray-700">{cluster.name}</span>
                        <span className={`text-xs px-1.5 py-0.5 rounded border ${SENTIMENT_COLOR[cluster.sentiment] || SENTIMENT_COLOR.neutre}`}>
                          {SENTIMENT_ICON[cluster.sentiment] || "😐"} {cluster.sentiment}
                        </span>
                      </div>
                      {cluster.sub_clusters?.map((sc, j) => (
                        <div key={j} className="flex items-center gap-2 ml-3 mt-0.5">
                          <span className="text-xs text-gray-500">↳ {sc.name}</span>
                          <span className={`text-xs px-1 rounded border ${SENTIMENT_COLOR[sc.sentiment] || SENTIMENT_COLOR.neutre}`}>
                            {SENTIMENT_ICON[sc.sentiment] || "😐"}
                          </span>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Relancer */}
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" />
            Relancer l'analyse
          </button>
        </div>
      )}

      {/* Erreur */}
      {analysis?.status === "failed" && (
        <p className="text-xs text-red-500 bg-red-50 rounded p-2 mb-2">
          {analysis.error_message || "Analyse échouée"}
        </p>
      )}

      {/* En cours */}
      {(loading || analysis?.status === "processing") && (
        <div className="flex items-center gap-2 text-xs text-violet-600">
          <div className="w-3 h-3 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
          Analyse en cours…
        </div>
      )}

      {/* Formulaire de déclenchement */}
      {(!analysis || analysis.status === "failed" || expanded) && !loading && (
        <div className="flex items-center gap-2 mt-2">
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="flex-1 text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white focus:outline-none focus:border-violet-400"
          >
            <option value="">— Sélectionner un projet —</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.brand} · {p.name}
              </option>
            ))}
          </select>
          <button
            onClick={handleAnalyze}
            disabled={!selectedProject}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-violet-600 text-white rounded-lg hover:bg-violet-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <Brain className="w-3.5 h-3.5" />
            Analyser
          </button>
        </div>
      )}

      {projects.length === 0 && !analysis && (
        <p className="text-xs text-gray-400 mt-1">
          Aucun projet configuré.{" "}
          <a href="/projects" className="text-violet-500 hover:underline">
            Créer un projet
          </a>
        </p>
      )}
    </div>
  );
}
