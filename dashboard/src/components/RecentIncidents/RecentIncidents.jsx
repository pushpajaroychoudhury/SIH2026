import { AlertTriangle, Droplet, Car, TrafficCone, Bus } from "lucide-react";
import "./RecentIncidents.css";

const ICONS = {
  pothole: { icon: AlertTriangle, tone: "red" },
  waterlogging: { icon: Droplet, tone: "blue" },
  congestion: { icon: Car, tone: "amber" },
  infrastructure: { icon: TrafficCone, tone: "purple" },
  bus_delay: { icon: Bus, tone: "amber" },
};

export default function RecentIncidents({ incidents = [], loading }) {
  return (
    <div className="recent-incidents card">
      <div className="ri-header">
        <span>Recent Incidents</span>
        <button className="ri-view-all">View All</button>
      </div>

      <div className="ri-list">
        {loading && !incidents.length
          ? Array.from({ length: 5 }).map((_, i) => <div key={i} className="ri-item skeleton" />)
          : incidents.map((inc) => {
              const meta = ICONS[inc.type] || ICONS.pothole;
              const Icon = meta.icon;
              return (
                <div key={inc.id} className="ri-item">
                  <span className={`ri-icon tone-${meta.tone}`}>
                    <Icon size={15} />
                  </span>
                  <div className="ri-body">
                    <div className="ri-title">{inc.title}</div>
                    <div className="ri-location">{inc.location}</div>
                    <div className="ri-time">{inc.minutes_ago} mins ago</div>
                  </div>
                  <span className={`badge badge-${inc.severity}`}>
                    {inc.severity.toUpperCase()}
                  </span>
                </div>
              );
            })}
      </div>
    </div>
  );
}
