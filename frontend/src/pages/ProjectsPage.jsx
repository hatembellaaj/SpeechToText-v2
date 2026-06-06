import { useState, useEffect } from "react";
import { Plus, Trash2, ChevronDown, ChevronUp, BarChart2, Users } from "lucide-react";
import { projectsApi } from "../api/client";

const PROFILE_COLORS = [
  "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#9CA3AF"
];

const THERMOR_PROFILES = [
  {
    name: "Conquête",
    description: "Non-client Thermor effectuant son premier achat (toutes familles). L'installateur n'a jamais travaillé avec Thermor ou découvre la marque pour la première fois. Il pose des questions de base sur les produits, les prix, les démarches pour référencer Thermor.",
    keywords: "premier achat, nouveau client, référencement, découverte, jamais commandé",
    color: "#10B981", order: 1, is_neutral: false,
  },
  {
    name: "Change",
    description: "Client Thermor existant sur certaines familles, qui démarre sur une nouvelle famille de produits. Il a une relation avec Thermor mais aborde une technicité nouvelle (ex. client radiateurs qui installe sa première PAC Thermor).",
    keywords: "nouvelle famille, première installation, formation, montée en gamme",
    color: "#3B82F6", order: 2, is_neutral: false,
  },
  {
    name: "Cross sell",
    description: "Installateur actif sur une famille de produits mais chez un concurrent, qui démarre cette famille avec Thermor. Il maîtrise la technicité mais veut changer de marque, souvent après des problèmes SAV chez la concurrence.",
    keywords: "changement de marque, concurrent, SAV concurrent, tester Thermor, migration",
    color: "#8B5CF6", order: 3, is_neutral: false,
  },
  {
    name: "Hausse d'usage",
    description: "Client Thermor existant dont la part d'achats Thermor augmente sur une ou plusieurs familles. Il est satisfait, accroît sa fidélité, réduit sa part concurrente. Peut négocier de meilleures conditions commerciales.",
    keywords: "augmentation volume, fidélisation, satisfaction, conditions commerciales",
    color: "#F59E0B", order: 4, is_neutral: false,
  },
  {
    name: "Baisse d'usage",
    description: "Client Thermor existant dont la part d'achats diminue sur une ou plusieurs familles. Il s'oriente vers des concurrents, souvent pour des raisons de prix ou d'insatisfaction partielle. Reste encore client mais montre des signaux de désengagement.",
    keywords: "réduction volume, concurrent moins cher, remise, insatisfaction partielle",
    color: "#EF4444", order: 5, is_neutral: false,
  },
  {
    name: "Churn",
    description: "Client qui a arrêté ou envisage d'arrêter complètement Thermor sur une famille ou toutes les familles. Insatisfaction forte, souvent liée à des problèmes SAV répétés ou une perte de confiance. La relation commerciale est rompue ou en voie de l'être.",
    keywords: "arrêt commandes, perte confiance, SAV problème, basculé concurrent, rupture",
    color: "#DC2626", order: 6, is_neutral: false,
  },
  {
    name: "Non catégorisé",
    description: "Le comportement du client ne correspond clairement à aucun des 6 profils. Conversation trop courte, hors-sujet, ou ne contient pas assez d'éléments pour identifier une intention commerciale. Ex : demande administrative, question technique sans contexte.",
    keywords: "neutre, indéterminé, hors sujet, question technique, administratif",
    color: "#9CA3AF", order: 7, is_neutral: true,
  },
];

function ProfileRow({ profile, onDelete }) {
  return (
    <div className="flex items-start gap-3 py-2 border-b border-gray-50 last:border-0">
      <div
        className="w-3 h-3 rounded-full mt-1 shrink-0"
        style={{ backgroundColor: profile.color }}
      />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-800">{profile.name}</p>
        <p className="text-xs text-gray-400 leading-relaxed">{profile.description}</p>
      </div>
      {onDelete && (
        <button onClick={() => onDelete(profile.id)} className="text-gray-300 hover:text-red-400 mt-0.5">
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}

function ProjectCard({ project, onDelete }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <div className="flex items-center gap-3 p-4">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <p className="font-semibold text-gray-900">{project.name}</p>
            <span className="text-xs px-2 py-0.5 bg-sky-50 text-sky-700 border border-sky-200 rounded-full">
              {project.brand}
            </span>
          </div>
          {project.description && (
            <p className="text-xs text-gray-400 mt-0.5">{project.description}</p>
          )}
          <p className="text-xs text-gray-300 mt-0.5">
            {project.profiles?.length || 0} profils
          </p>
        </div>
        <div className="flex items-center gap-2">
          <a
            href={`/projects/${project.id}/stats`}
            className="flex items-center gap-1 text-xs px-2 py-1.5 border border-violet-200 text-violet-600 rounded-lg hover:bg-violet-50"
          >
            <BarChart2 className="w-3.5 h-3.5" />
            Stats
          </a>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-gray-400 hover:text-gray-600 p-1"
          >
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          <button onClick={() => onDelete(project.id)} className="text-gray-300 hover:text-red-400 p-1">
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {expanded && project.profiles?.length > 0 && (
        <div className="px-4 pb-4 border-t border-gray-50 pt-3">
          {project.profiles.map((p) => (
            <ProfileRow key={p.id} profile={p} />
          ))}
        </div>
      )}
    </div>
  );
}

function CreateProjectModal({ onClose, onCreate }) {
  const [name, setName] = useState("");
  const [brand, setBrand] = useState("Thermor");
  const [description, setDescription] = useState("");
  const [useThermor, setUseThermor] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    try {
      const profiles = useThermor ? THERMOR_PROFILES : [];
      await onCreate({ name, brand, description, profiles });
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg">
        <div className="p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Nouveau projet</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Nom du projet *</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="ex: Thermor SAV Q2 2026"
                className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Marque</label>
              <input
                type="text"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                placeholder="Thermor, Atlantic..."
                className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
                className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:border-violet-400"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="useThermor"
                checked={useThermor}
                onChange={(e) => setUseThermor(e.target.checked)}
                className="rounded"
              />
              <label htmlFor="useThermor" className="text-sm text-gray-600">
                Utiliser le référentiel Thermor (6 profils + Neutre)
              </label>
            </div>
            {useThermor && (
              <div className="bg-gray-50 rounded-lg p-3 max-h-40 overflow-y-auto">
                {THERMOR_PROFILES.map((p, i) => (
                  <div key={i} className="flex items-center gap-2 py-0.5">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }} />
                    <span className="text-xs text-gray-600 font-medium">{p.name}</span>
                    {p.is_neutral && <span className="text-xs text-gray-400">(neutre)</span>}
                  </div>
                ))}
              </div>
            )}
            <div className="flex gap-2 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={loading || !name.trim()}
                className="flex-1 py-2 text-sm bg-violet-600 text-white rounded-lg hover:bg-violet-700 disabled:opacity-50"
              >
                {loading ? "Création…" : "Créer"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectsApi.list()
      .then(setProjects)
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (data) => {
    const project = await projectsApi.create(data);
    setProjects((prev) => [project, ...prev]);
  };

  const handleDelete = async (id) => {
    if (!confirm("Supprimer ce projet et toutes ses analyses ?")) return;
    await projectsApi.delete(id);
    setProjects((prev) => prev.filter((p) => p.id !== id));
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-violet-500" />
          <h1 className="text-xl font-bold text-gray-900">Projets PROFILER</h1>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-1.5 px-4 py-2 bg-violet-600 text-white text-sm rounded-xl hover:bg-violet-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Nouveau projet
        </button>
      </div>

      {loading ? (
        <p className="text-center text-gray-400 py-12">Chargement…</p>
      ) : projects.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <Users className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p className="text-sm">Aucun projet. Créez-en un pour commencer l'analyse.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map((p) => (
            <ProjectCard key={p.id} project={p} onDelete={handleDelete} />
          ))}
        </div>
      )}

      {showModal && (
        <CreateProjectModal
          onClose={() => setShowModal(false)}
          onCreate={handleCreate}
        />
      )}
    </div>
  );
}
