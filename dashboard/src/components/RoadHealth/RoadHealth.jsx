import "./RoadHealth.css";

export default function RoadHealth({ roads = [], totalSegments, loading }) {
  return (
    <div className="road-health card">
      <div className="rh-header">
        <span>Road Health Overview</span>
        <button className="rh-view-details">View Details</button>
      </div>

      <div className="rh-list">
        {loading && !roads.length
          ? Array.from({ length: 5 }).map((_, i) => <div key={i} className="rh-item skeleton" />)
          : roads.map((r) => (
              <div key={r.road} className="rh-item">
                <div className="rh-row-top">
                  <span className="rh-name">{r.road}</span>
                  <span className="rh-pct">{r.risk_pct}%</span>
                  <span className={`badge badge-${r.level}`}>
                    {r.level === "high" ? "High Risk" : r.level === "medium" ? "Medium Risk" : "Low Risk"}
                  </span>
                </div>
                <div className="rh-bar-track">
                  <div
                    className={`rh-bar-fill level-${r.level}`}
                    style={{ width: `${r.risk_pct}%` }}
                  />
                </div>
              </div>
            ))}
      </div>

      <div className="rh-footer">
        <span>Total Road Segments Monitored</span>
        <span className="rh-footer-value">{totalSegments}</span>
      </div>
    </div>
  );
}
