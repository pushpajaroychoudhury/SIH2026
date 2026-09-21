# SIH26124 — Bridge Backend

This is what connects `edge-ai` and `dashboard` together. Without it,
they're two projects that don't know about each other.

## What it actually does right now

**Real, working:**
`vehicle_counter.py` detects a car/bus/truck/motorcycle → POSTs it here →
this server buckets it into a 15-minute time slot → the dashboard's
**Traffic Flow chart** fetches it and displays it. That whole chain is
real and tested.

**Still mock (clearly marked in `main.py`):**
Bus delays, the OD matrix, and incident types — because the detectors for
those (waterlogging, potholes, incidents) either aren't trained yet or
aren't wired up to send data anywhere yet. This backend doesn't pretend
otherwise; look at `main.py`, everything fake is in functions named
`_mock_*`.

This is intentionally a small stepping stone, not the final backend. The
folder structure from earlier (`backend/fastapi-service/` with MongoDB,
proper routers, etc.) is still the real target once more detectors exist
and you need to persist data instead of holding it in memory.

## Run it

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Leave this running at `http://localhost:8000` — both the dashboard and
`vehicle_counter.py` talk to it.

Check it's alive: open `http://localhost:8000/docs` in a browser — that's
FastAPI's automatic interactive API docs, useful for testing endpoints by
hand.

## How the three pieces fit together

```
vehicle_counter.py  --POST-->  backend (this)  <--GET--  dashboard
  (edge-ai)                    :8000                     :5173
```

1. Start this backend first (`uvicorn main:app --reload --port 8000`)
2. Start the dashboard (`npm run dev` in `dashboard/`) — it'll immediately
   start polling `/api/analytics/traffic` every few seconds
3. Start `vehicle_counter.py` pointed at a traffic video — every vehicle
   it counts posts here automatically (it already defaults to
   `http://localhost:8000`, no flag needed unless you changed the port)
4. Watch the dashboard's **Traffic Flow** chart update with real numbers
   as the video plays

If you start them in a different order, it still works — `vehicle_counter.py`
silently skips sending if the backend isn't up yet (see `_send_to_backend`),
and the dashboard falls back to mock data if this backend isn't reachable
(see `USE_REAL_TRAFFIC_DATA` in `dashboard/src/services/api.js`). Nothing
crashes if you start things out of order — it just won't show real data
until all three are running.
