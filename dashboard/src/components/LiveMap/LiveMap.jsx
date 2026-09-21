import { useState } from "react";
import {
  Maximize2,
  Plus,
  Minus,
  Navigation,
  Layers,
  AlertTriangle,
  Droplet,
  Car,
  Milestone,
  Bus,
} from "lucide-react";
import "./LiveMap.css";

const MARKER_META = {
  pothole: { icon: AlertTriangle, tone: "red", label: "Pothole / Road Defect" },
  waterlogging: { icon: Droplet, tone: "blue", label: "Waterlogging" },
  congestion: { icon: Car, tone: "amber", label: "Congestion" },
  infrastructure: { icon: Milestone, tone: "purple", label: "Infrastructure Issue" },
  bus: { icon: Bus, tone: "green", label: "Bus (Live)" },
  risk_zone: { icon: null, tone: "red", label: "Risk Zone" },
};

export default function LiveMap({ markers = [], landmarks = [], loading }) {
  const [view, setView] = useState("map");
  const [zoom, setZoom] = useState(1);

  return (
    <div className="live-map card">
      <div className="live-map-header">
        <div className="live-map-title">
          <span>Live Urban Map</span>
          <span className="live-dot-label">
            <span className="live-dot" /> Real-time data
          </span>
        </div>
        <div className="live-map-toggle">
          <button className={view === "map" ? "active" : ""} onClick={() => setView("map")}>
            Map
          </button>
          <button
            className={view === "satellite" ? "active" : ""}
            onClick={() => setView("satellite")}
          >
            Satellite
          </button>
        </div>
      </div>

      <div className="live-map-body">
        <div className="map-legend card">
          {Object.entries(MARKER_META).map(([key, { icon: Icon, tone, label }]) => (
            <div key={key} className="legend-row">
              <span className={`legend-dot tone-${tone}`}>
                {Icon ? <Icon size={11} /> : null}
              </span>
              <span>{label}</span>
            </div>
          ))}
        </div>

        <div
          className={`map-canvas ${view === "satellite" ? "satellite" : ""}`}
          style={{ transform: `scale(${zoom})` }}
        >
          <svg className="map-roads" viewBox="0 0 100 100" preserveAspectRatio="none">
            <path d="M0,45 L100,40" className="road-main" />
            <path d="M0,65 L100,72" className="road-main" />
            <path d="M20,0 L28,100" className="road-main" />
            <path d="M55,0 L48,100" className="road-main" />
            <path d="M0,20 L100,58" className="road-minor" />
            <path d="M0,80 L100,30" className="road-minor" />
          </svg>

          {landmarks.map((l) => (
            <div
              key={l.id}
              className="map-landmark"
              style={{ left: `${l.x}%`, top: `${l.y}%` }}
            >
              {l.label}
            </div>
          ))}

          {markers.map((m) => {
            const meta = MARKER_META[m.type] || MARKER_META.pothole;
            const Icon = meta.icon;
            return (
              <div
                key={m.id}
                className={`map-marker tone-${meta.tone} ${m.radius ? "risk-radius" : ""}`}
                style={{ left: `${m.x}%`, top: `${m.y}%` }}
                title={m.label}
              >
                {Icon && <Icon size={12} />}
              </div>
            );
          })}

          {loading && <div className="map-loading">Loading live data…</div>}
        </div>

        <div className="map-controls">
          <button className="map-control-btn" title="Layers">
            <Layers size={16} />
          </button>
          <div className="map-zoom-group">
            <button onClick={() => setZoom((z) => Math.min(z + 0.15, 1.6))}>
              <Plus size={14} />
            </button>
            <button onClick={() => setZoom((z) => Math.max(z - 0.15, 0.8))}>
              <Minus size={14} />
            </button>
          </div>
          <button className="map-control-btn" title="Recenter" onClick={() => setZoom(1)}>
            <Navigation size={14} />
          </button>
        </div>

        <button className="map-fullscreen-btn" title="Fullscreen">
          <Maximize2 size={14} />
        </button>
      </div>
    </div>
  );
}
