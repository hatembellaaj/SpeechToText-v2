import { NavLink } from "react-router-dom";
import { Mic, History, Activity } from "lucide-react";

export default function Navbar() {
  const linkClass = ({ isActive }) =>
    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? "bg-sky-100 text-sky-700"
        : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
    }`;

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Mic className="w-5 h-5 text-sky-600" />
          <span className="font-semibold text-gray-900">SpeechToText</span>
          <span className="text-xs text-gray-400 font-normal ml-1">Thermor</span>
        </div>
        <nav className="flex items-center gap-1">
          <NavLink to="/" end className={linkClass}>
            <Activity className="w-4 h-4" />
            Dashboard
          </NavLink>
          <NavLink to="/history" className={linkClass}>
            <History className="w-4 h-4" />
            Historique
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
