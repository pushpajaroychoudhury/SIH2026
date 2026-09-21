import { Fragment, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import "./TrafficAnalytics.css";

const RANGES = ["1H", "6H", "24H", "7D"];

function odColor(value) {
  // 0-100 -> blue (low) to red (high), matching the mockup's heat scale
  const stops = [
    { v: 0, c: [59, 130, 246] },
    { v: 50, c: [245, 158, 11] },
    { v: 100, c: [239, 68, 68] },
  ];
  let lo = stops[0], hi = stops[stops.length - 1];
  for (let i = 0; i < stops.length - 1; i++) {
    if (value >= stops[i].v && value <= stops[i + 1].v) {
      lo = stops[i];
      hi = stops[i + 1];
      break;
    }
  }
  const t = (value - lo.v) / (hi.v - lo.v || 1);
  const rgb = lo.c.map((c, i) => Math.round(c + (hi.c[i] - c) * t));
  return `rgb(${rgb.join(",")})`;
}

export default function TrafficAnalytics({ data, range, onRangeChange, loading }) {
  const [tab, setTab] = useState(range || "24H");

  const handleRange = (r) => {
    setTab(r);
    onRangeChange?.(r);
  };

  if (loading || !data) {
    return <div className="traffic-analytics card skeleton-block" />;
  }

  const { traffic_flow, bus_delays, od_matrix, incident_types, incident_total } = data;

  return (
    <div className="traffic-analytics card">
      <div className="ta-header">
        <span className="ta-title">Traffic &amp; Fleet Analytics</span>
        <div className="ta-range-toggle">
          {RANGES.map((r) => (
            <button key={r} className={tab === r ? "active" : ""} onClick={() => handleRange(r)}>
              {r}
            </button>
          ))}
        </div>
      </div>

      <div className="ta-grid">
        <div className="ta-chart-block">
          <div className="ta-block-title">
            Traffic Flow
            <span className="legend-inline">
              <i className="dot tone-blue" /> Vehicles
              <i className="dot tone-green" /> Buses
            </span>
          </div>
          <ResponsiveContainer width="100%" height={150}>
            <LineChart data={traffic_flow}>
              <CartesianGrid stroke="#1f2a44" vertical={false} />
              <XAxis dataKey="time" stroke="#5c6a8c" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis stroke="#5c6a8c" fontSize={10} tickLine={false} axisLine={false} width={32} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="vehicles" stroke="#3b82f6" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="buses" stroke="#22c55e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="ta-chart-block">
          <div className="ta-block-title">Bus Delays (min)</div>
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={bus_delays}>
              <CartesianGrid stroke="#1f2a44" vertical={false} />
              <XAxis dataKey="time" stroke="#5c6a8c" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis stroke="#5c6a8c" fontSize={10} tickLine={false} axisLine={false} width={28} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="delay" fill="#f59e0b" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="ta-chart-block">
          <div className="ta-block-title">Origin – Destination Analysis</div>
          <div className="od-matrix">
            <div className="od-grid" style={{ gridTemplateColumns: `54px repeat(${od_matrix.zones.length}, 1fr)` }}>
              <div />
              {od_matrix.zones.map((z) => (
                <div key={z} className="od-col-label">{z}</div>
              ))}
              {od_matrix.matrix.map((row, i) => (
                <Fragment key={`row-${i}`}>
                  <div className="od-row-label">{od_matrix.zones[i]}</div>
                  {row.map((v, j) => (
                    <div
                      key={`${i}-${j}`}
                      className="od-cell"
                      style={{ background: odColor(v) }}
                      title={`${od_matrix.zones[i]} → ${od_matrix.zones[j]}: ${v}`}
                    />
                  ))}
                </Fragment>
              ))}
            </div>
          </div>
        </div>

        <div className="ta-chart-block">
          <div className="ta-block-title">Incident Types</div>
          <div className="incident-donut-row">
            <ResponsiveContainer width={120} height={120}>
              <PieChart>
                <Pie
                  data={incident_types}
                  dataKey="value"
                  nameKey="type"
                  innerRadius={38}
                  outerRadius={56}
                  paddingAngle={2}
                >
                  {incident_types.map((entry) => (
                    <Cell key={entry.type} fill={entry.color} stroke="none" />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="donut-center-label">
              <div className="donut-total">{incident_total}</div>
              <div className="donut-caption">Total</div>
            </div>
            <div className="donut-legend">
              {incident_types.map((t) => (
                <div key={t.type} className="donut-legend-row">
                  <i className="dot" style={{ background: t.color }} />
                  <span>{t.type}</span>
                  <span className="donut-legend-value">{t.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const tooltipStyle = {
  background: "#151f38",
  border: "1px solid #2a3a5c",
  borderRadius: 8,
  fontSize: 12,
  color: "#eef2fb",
};
