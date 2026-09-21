# SIH26124 — Dashboard (Urban Intelligence)

React + Vite frontend for the central authority dashboard: live map,
incident feed, traffic/fleet analytics, road health, and an AI assistant
panel — matching the approved UI design.

## Folder contents

```
dashboard/
├── src/
│   ├── components/
│   │   ├── Sidebar/            # left nav
│   │   ├── TopBar/              # search, notifications, admin profile
│   │   ├── StatsCards/          # 5 top metric cards
│   │   ├── LiveMap/             # stylized map with incident/bus markers
│   │   ├── RecentIncidents/     # right-hand incident feed
│   │   ├── TrafficAnalytics/    # traffic flow, bus delays, OD matrix, incident donut
│   │   ├── RoadHealth/          # per-road risk bars
│   │   └── AIAssistant/         # chat panel with suggested prompts
│   ├── pages/
│   │   └── Dashboard.jsx        # composes everything into the mockup layout
│   ├── services/
│   │   └── api.js               # ⭐ the ONLY file that talks to the backend
│   ├── hooks/
│   │   └── useLiveData.js       # polling hook (swap for WebSocket later)
│   ├── data/
│   │   └── mockData.js          # mock dataset shaped like the real API responses
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css                # design tokens + base styles
├── index.html
├── package.json
└── vite.config.js
```

## Setup

```bash
cd dashboard
npm install
npm run dev
```

Opens at `http://localhost:5173`. Runs entirely on mock data out of the box
— no backend required.

## Connecting the real backend

Everything the dashboard needs from the backend goes through
**`src/services/api.js`**. Every function there already:
- Returns the exact shape the components expect
- Has a `fetch()` branch already written, pointing at the endpoint the
  FastAPI backend should expose (see comments in that file)

To go live:
1. In `src/services/api.js`, set `USE_MOCK = false`
2. Set `BASE_URL` to your FastAPI service's address
3. Make sure the backend's response JSON matches the shapes documented in
   `src/data/mockData.js` — that file IS the API contract for now

No component files need to change. That's the whole point of the service
layer split.

## What's simulated vs. real right now
- **Polling, not push**: `useLiveData` re-fetches on an interval to fake
  real-time updates. Swap it for a WebSocket subscription once the backend
  supports push — components don't need to change.
- **AI Assistant** gives a canned placeholder response. Wire
  `askAssistant()` in `api.js` to a real endpoint once the backend has one.
- **Map** is a stylized abstract layout (matches the mockup's illustrated
  style), not real map tiles. If you want real GIS tiles/geo-accurate
  positioning later, swap `LiveMap.jsx`'s canvas for a Leaflet/Mapbox
  integration — marker data already carries lat/lon-ready fields once the
  backend sends them.

## Verified
`npm install && npm run build` completes clean with no errors.
