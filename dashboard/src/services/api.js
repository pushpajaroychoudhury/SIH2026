// Single place the dashboard talks to the backend.
// Every function here returns the SAME shape whether it's mocked or real,
// so no component ever needs to change when the backend comes online.
//
// TO GO LIVE:
//   1. Set USE_MOCK = false
//   2. Set BASE_URL to your FastAPI service (e.g. http://localhost:8000/api)
//   3. Delete/ignore the mock branches below - the fetch() branches already
//      call the endpoints the backend README documents.

import {
  mockStats,
  mockMapMarkers,
  mockLandmarks,
  mockRecentIncidents,
  mockTrafficFlow,
  mockBusDelays,
  mockODMatrix,
  mockIncidentTypes,
  mockIncidentTotal,
  mockRoadHealth,
  mockTotalRoadSegments,
} from "../data/mockData";

const USE_MOCK = true;
const BASE_URL = "http://localhost:8000/api";

// Traffic analytics is special: the bridge backend (backend/main.py) is
// now live and serving REAL vehicle counts from vehicle_counter.py, so
// this one ignores USE_MOCK and always tries the real endpoint first -
// falling back to mock data only if the backend isn't running, so the
// dashboard never breaks if you forget to start it.
const USE_REAL_TRAFFIC_DATA = true;

// simulate realistic network latency so loading states are visible in dev
const delay = (ms = 350) => new Promise((res) => setTimeout(res, ms));

async function getJSON(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status} on ${path}`);
  return res.json();
}

export async function fetchStats() {
  if (USE_MOCK) {
    await delay();
    return mockStats;
  }
  return getJSON("/dashboard/stats");
}

export async function fetchMapData() {
  if (USE_MOCK) {
    await delay();
    return { markers: mockMapMarkers, landmarks: mockLandmarks };
  }
  return getJSON("/map/live");
}

export async function fetchRecentIncidents(limit = 6) {
  if (USE_MOCK) {
    await delay();
    return mockRecentIncidents.slice(0, limit);
  }
  return getJSON(`/incidents/recent?limit=${limit}`);
}

export async function fetchTrafficAnalytics(range = "24H") {
  if (USE_REAL_TRAFFIC_DATA) {
    try {
      return await getJSON(`/analytics/traffic?range=${range}`);
    } catch {
      // bridge backend not running - fall through to mock so the chart
      // still renders instead of showing a broken/empty panel
    }
  }
  await delay();
  return {
    traffic_flow: mockTrafficFlow,
    bus_delays: mockBusDelays,
    od_matrix: mockODMatrix,
    incident_types: mockIncidentTypes,
    incident_total: mockIncidentTotal,
  };
}

export async function fetchRoadHealth() {
  if (USE_MOCK) {
    await delay();
    return { roads: mockRoadHealth, total_segments: mockTotalRoadSegments };
  }
  return getJSON("/road-health");
}

// AI Assistant - placeholder until the backend wires this to an LLM over
// the incident/analytics data. Echoes a canned response per prompt so the
// UI is fully clickable during the demo.
export async function askAssistant(question) {
  if (USE_MOCK) {
    await delay(600);
    return {
      question,
      answer:
        "This will be answered by the backend once it's connected — it'll query live incident and road-health data to respond.",
    };
  }
  const res = await fetch(`${BASE_URL}/assistant/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`Assistant error ${res.status}`);
  return res.json();
}
