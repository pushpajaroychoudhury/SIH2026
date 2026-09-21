// Mock data shaped exactly like what GET /api/dashboard/summary and friends
// will return from the FastAPI backend once it's wired up. Keeping the
// shape identical now means swapping services/api.js later requires no
// component changes.

export const mockStats = {
  active_buses: { value: 128, change_pct: 12, trend: "up" },
  total_incidents: { value: 342, change_pct: 8, trend: "up" },
  critical_incidents: { value: 17, change_pct: 25, trend: "up" },
  road_risk_score: { value: 64, unit: "%", change_pct: 6, trend: "up" },
  avg_bus_delay: { value: 28, unit: "min", change_pct: 18, trend: "down" },
};

// Positions are percentages of the map container (0-100), so the map
// layout stays responsive without needing real lat/lon + tile projection.
export const mockMapMarkers = [
  { id: "m1", type: "pothole", label: "Pothole Detected", x: 22, y: 38 },
  { id: "m2", type: "infrastructure", label: "Traffic Signal Fault", x: 34, y: 36 },
  { id: "m3", type: "pothole", label: "Pothole Detected", x: 28, y: 62 },
  { id: "m4", type: "bus", label: "Bus 42", x: 18, y: 58 },
  { id: "m5", type: "bus", label: "Bus 17", x: 45, y: 45 },
  { id: "m6", type: "congestion", label: "Heavy Congestion", x: 40, y: 68 },
  { id: "m7", type: "bus", label: "Bus 09", x: 55, y: 30 },
  { id: "m8", type: "pothole", label: "Pothole Detected", x: 60, y: 55 },
  { id: "m9", type: "bus", label: "Bus 23", x: 65, y: 22 },
  { id: "m10", type: "waterlogging", label: "Waterlogging", x: 72, y: 58 },
  { id: "m11", type: "pothole", label: "Pothole Detected", x: 58, y: 78 },
  { id: "m12", type: "risk_zone", label: "Risk Zone — MG Road", x: 40, y: 52, radius: true },
];

export const mockLandmarks = [
  { id: "l1", label: "Riverside Park", x: 30, y: 15 },
  { id: "l2", label: "Central Station", x: 52, y: 25 },
  { id: "l3", label: "Tech Park", x: 78, y: 30 },
  { id: "l4", label: "City Mall", x: 42, y: 40 },
  { id: "l5", label: "Green Valley", x: 18, y: 70 },
];

export const mockRecentIncidents = [
  { id: "i1", type: "pothole", title: "Pothole Detected", location: "MG Road (Near Central Station)", minutes_ago: 12, severity: "high" },
  { id: "i2", type: "waterlogging", title: "Waterlogging", location: "Riverside Road", minutes_ago: 18, severity: "medium" },
  { id: "i3", type: "congestion", title: "Heavy Congestion", location: "Park Street", minutes_ago: 25, severity: "high" },
  { id: "i4", type: "infrastructure", title: "Traffic Signal Fault", location: "Tech Park Junction", minutes_ago: 32, severity: "medium" },
  { id: "i5", type: "pothole", title: "Pothole Detected", location: "Green Valley Road", minutes_ago: 41, severity: "high" },
  { id: "i6", type: "bus_delay", title: "Bus Delay", location: "Route 42 – City Mall", minutes_ago: 52, severity: "medium" },
];

export const mockTrafficFlow = [
  { time: "00:00", vehicles: 180, buses: 40 },
  { time: "04:00", vehicles: 220, buses: 55 },
  { time: "08:00", vehicles: 980, buses: 210 },
  { time: "12:00", vehicles: 760, buses: 180 },
  { time: "16:00", vehicles: 1120, buses: 240 },
  { time: "20:00", vehicles: 640, buses: 150 },
  { time: "24:00", vehicles: 260, buses: 60 },
];

export const mockBusDelays = [
  { time: "00:00", delay: 4 }, { time: "02:00", delay: 6 }, { time: "04:00", delay: 5 },
  { time: "06:00", delay: 12 }, { time: "08:00", delay: 28 }, { time: "10:00", delay: 22 },
  { time: "12:00", delay: 18 }, { time: "14:00", delay: 20 }, { time: "16:00", delay: 30 },
  { time: "18:00", delay: 34 }, { time: "20:00", delay: 24 }, { time: "22:00", delay: 14 },
  { time: "24:00", delay: 8 },
];

export const mockODMatrix = {
  zones: ["Central", "North", "East", "West", "South"],
  // matrix[i][j] = trip volume from zones[i] to zones[j], 0-100 scale
  matrix: [
    [10, 65, 40, 55, 70],
    [60, 15, 80, 35, 45],
    [45, 75, 20, 90, 30],
    [55, 40, 85, 18, 60],
    [68, 50, 35, 65, 22],
  ],
};

export const mockIncidentTypes = [
  { type: "Pothole", value: 38, color: "#ef4444" },
  { type: "Waterlogging", value: 22, color: "#3b82f6" },
  { type: "Congestion", value: 18, color: "#f59e0b" },
  { type: "Infrastructure", value: 12, color: "#a855f7" },
  { type: "Others", value: 10, color: "#94a3b8" },
];
export const mockIncidentTotal = 342;

export const mockRoadHealth = [
  { road: "MG Road", risk_pct: 78, level: "high" },
  { road: "Riverside Road", risk_pct: 65, level: "high" },
  { road: "Park Street", risk_pct: 52, level: "medium" },
  { road: "Tech Park Road", risk_pct: 38, level: "medium" },
  { road: "Green Valley Road", risk_pct: 21, level: "low" },
];
export const mockTotalRoadSegments = 125;

export const mockAssistantPrompts = [
  "How many persistent potholes were detected this week?",
  "Which routes have the highest delays?",
  "Show critical incidents near schools.",
  "Which road segments are at high risk?",
];
