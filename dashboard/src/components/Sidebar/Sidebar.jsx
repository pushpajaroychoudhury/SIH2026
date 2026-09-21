import {
  LayoutDashboard,
  MapPin,
  AlertTriangle,
  Activity,
  Bus,
  TrendingUp,
  BarChart3,
  FileText,
  MessageSquare,
  Settings,
} from "lucide-react";
import "./Sidebar.css";

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "live-map", label: "Live Map", icon: MapPin },
  { id: "incidents", label: "Incidents", icon: AlertTriangle },
  { id: "road-health", label: "Road Health", icon: Activity },
  { id: "fleet", label: "Fleet Monitoring", icon: Bus },
  { id: "routes", label: "Route Analytics", icon: TrendingUp },
  { id: "predictions", label: "Predictions", icon: BarChart3 },
  { id: "reports", label: "Reports", icon: FileText },
  { id: "assistant", label: "AI Assistant", icon: MessageSquare },
];

export default function Sidebar({ activeItem = "dashboard", onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">
          <Bus size={20} />
        </div>
        <div>
          <div className="sidebar-brand-name">Urban Intelligence</div>
          <div className="sidebar-brand-sub">AI-Powered Urban Mobility</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={`sidebar-link ${activeItem === id ? "active" : ""}`}
            onClick={() => onNavigate?.(id)}
          >
            <Icon size={18} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <button
        className={`sidebar-link settings-link ${activeItem === "settings" ? "active" : ""}`}
        onClick={() => onNavigate?.("settings")}
      >
        <Settings size={18} />
        <span>Settings</span>
      </button>

      <div className="sidebar-footer-banner">
        <div className="sidebar-footer-tagline">
          Smarter Cities
          <br />
          Safer Roads
          <br />
          Better Mobility
        </div>
      </div>

      <div className="sidebar-problem-tag">
        <span className="sidebar-problem-code">SIH26124</span>
        <span className="sidebar-problem-label">Smart India Hackathon</span>
      </div>
    </aside>
  );
}
