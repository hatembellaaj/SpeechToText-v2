import { Loader2, CheckCircle2, XCircle, Clock } from "lucide-react";

const CONFIG = {
  pending:    { label: "En attente",      icon: Clock,        cls: "bg-gray-100 text-gray-600" },
  processing: { label: "En cours...",     icon: Loader2,      cls: "bg-sky-100 text-sky-700",  spin: true },
  completed:  { label: "Terminé",         icon: CheckCircle2, cls: "bg-green-100 text-green-700" },
  failed:     { label: "Échec",           icon: XCircle,      cls: "bg-red-100 text-red-700" },
};

export default function StatusBadge({ status }) {
  const cfg = CONFIG[status] || CONFIG.pending;
  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${cfg.cls}`}>
      <Icon className={`w-3.5 h-3.5 ${cfg.spin ? "animate-spin" : ""}`} />
      {cfg.label}
    </span>
  );
}
