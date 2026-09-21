import { Bus, AlertTriangle, ShieldAlert, Activity, Clock, ArrowUp, ArrowDown } from "lucide-react";
import "./StatsCards.css";

const ICONS = {
  active_buses: { icon: Bus, tone: "blue" },
  total_incidents: { icon: AlertTriangle, tone: "red" },
  critical_incidents: { icon: ShieldAlert, tone: "red" },
  road_risk_score: { icon: Activity, tone: "green" },
  avg_bus_delay: { icon: Clock, tone: "blue" },
};

const LABELS = {
  active_buses: "Active Buses",
  total_incidents: "Total Incidents",
  critical_incidents: "Critical Incidents",
  road_risk_score: "Road Risk Score",
  avg_bus_delay: "Average Bus Delay",
};

export default function StatsCards({ stats, loading }) {
  if (loading || !stats) {
    return (
      <div className="stats-row">
        {Object.keys(LABELS).map((key) => (
          <div key={key} className="stat-card card skeleton" />
        ))}
      </div>
    );
  }

  return (
    <div className="stats-row">
      {Object.entries(stats).map(([key, s]) => {
        const { icon: Icon, tone } = ICONS[key] || { icon: Activity, tone: "blue" };
        const TrendIcon = s.trend === "up" ? ArrowUp : ArrowDown;
        // for delay, "down" trend is good (green); for others "up" is typically the alert color already chosen
        const trendClass = key === "avg_bus_delay" && s.trend === "down" ? "trend-good" : `trend-${tone}`;

        return (
          <div key={key} className="stat-card card">
            <div className={`stat-icon tone-${tone}`}>
              <Icon size={18} />
            </div>
            <div className="stat-body">
              <div className="stat-label">{LABELS[key]}</div>
              <div className="stat-value-row">
                <span className="stat-value">
                  {s.value}
                  {s.unit || ""}
                </span>
                <span className={`stat-trend ${trendClass}`}>
                  <TrendIcon size={12} />
                  {s.change_pct}%
                </span>
              </div>
              <div className="stat-sub">vs. yesterday</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
