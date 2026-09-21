"""
SIH26124 - Bridge backend.

This is the piece that makes edge-ai and the dashboard actually talk to
each other. It's intentionally small (in-memory, no database) - the goal
right now is "prove the connection works end to end", not a production
backend. That's a bigger build for later (see README.md).

What it does:
  1. Receives real vehicle-count events POSTed from vehicle_counter.py
     every time it counts a new car/bus/truck/motorcycle.
  2. Buckets those counts into 15-minute time slots.
  3. Serves them at GET /api/analytics/traffic, in the EXACT shape the
     dashboard's src/services/api.js already expects (see mockData.js -
     that file IS the contract).
  4. Everything else (incidents, road health, bus delays) is still mock
     data here too, because those detectors don't exist yet - this
     backend is honest about only serving what's real.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
"""

from datetime import datetime, timezone
from collections import defaultdict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SIH26124 Bridge Backend")

# Allow the Vite dev server (dashboard) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------- #
# In-memory store. Resets every time you restart the server - that's
# fine for a demo, not fine for production (that's what the real
# FastAPI + MongoDB backend from the folder structure is for later).
# --------------------------------------------------------------------- #
vehicle_counts_by_slot: dict[str, dict[str, int]] = defaultdict(lambda: {"car": 0, "bus": 0, "motorcycle": 0, "truck": 0})


class VehicleCountEvent(BaseModel):
    label: str  # "car" | "bus" | "motorcycle" | "truck"
    count: int = 1


def _current_slot() -> str:
    """Buckets the current time into a 15-minute slot label like '14:15'."""
    now = datetime.now(timezone.utc)
    slot_minute = (now.minute // 15) * 15
    return f"{now.hour:02d}:{slot_minute:02d}"


@app.post("/api/edge/vehicle-count")
def receive_vehicle_count(event: VehicleCountEvent):
    """Called by vehicle_counter.py every time it counts a new vehicle."""
    slot = _current_slot()
    if event.label in vehicle_counts_by_slot[slot]:
        vehicle_counts_by_slot[slot][event.label] += event.count
    return {"ok": True, "slot": slot, "totals": vehicle_counts_by_slot[slot]}


@app.get("/api/analytics/traffic")
def get_traffic_analytics():
    """What the dashboard's Traffic & Fleet Analytics panel fetches.

    traffic_flow is REAL, built from vehicle_counter.py events.
    Everything else is still mock, clearly labeled as such below.
    """
    traffic_flow = []
    for slot in sorted(vehicle_counts_by_slot.keys()):
        counts = vehicle_counts_by_slot[slot]
        traffic_flow.append(
            {
                "time": slot,
                "vehicles": counts["car"] + counts["truck"] + counts["motorcycle"],
                "buses": counts["bus"],
            }
        )

    if not traffic_flow:
        # nothing received yet - keep the chart from being empty/broken
        traffic_flow = [{"time": _current_slot(), "vehicles": 0, "buses": 0}]

    return {
        "traffic_flow": traffic_flow,  # REAL DATA
        "bus_delays": _mock_bus_delays(),  # still mock - no delay detector yet
        "od_matrix": _mock_od_matrix(),  # still mock - no route/GPS tracking yet
        "incident_types": _mock_incident_types(),  # still mock - no incident detector wired up yet
        "incident_total": 0,
    }


@app.get("/api/edge/vehicle-count/summary")
def get_vehicle_count_summary():
    """Simple endpoint for debugging - see raw totals received so far."""
    totals = {"car": 0, "bus": 0, "motorcycle": 0, "truck": 0}
    for slot_counts in vehicle_counts_by_slot.values():
        for label, count in slot_counts.items():
            totals[label] += count
    return {"by_slot": dict(vehicle_counts_by_slot), "totals": totals}


# --------------------------------------------------------------------- #
# Mock helpers - kept obviously separate from the real data above so it's
# clear what still needs a real detector behind it.
# --------------------------------------------------------------------- #
def _mock_bus_delays():
    return [{"time": f"{h:02d}:00", "delay": 10 + (h % 6) * 4} for h in range(0, 25, 2)]


def _mock_od_matrix():
    zones = ["Central", "North", "East", "West", "South"]
    matrix = [[10, 65, 40, 55, 70], [60, 15, 80, 35, 45], [45, 75, 20, 90, 30],
              [55, 40, 85, 18, 60], [68, 50, 35, 65, 22]]
    return {"zones": zones, "matrix": matrix}


def _mock_incident_types():
    return [
        {"type": "Pothole", "value": 38, "color": "#ef4444"},
        {"type": "Waterlogging", "value": 22, "color": "#3b82f6"},
        {"type": "Congestion", "value": 18, "color": "#f59e0b"},
        {"type": "Infrastructure", "value": 12, "color": "#a855f7"},
        {"type": "Others", "value": 10, "color": "#94a3b8"},
    ]


@app.get("/")
def root():
    return {"status": "SIH26124 bridge backend running", "docs": "/docs"}
