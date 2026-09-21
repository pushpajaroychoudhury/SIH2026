import { useState } from "react";
import Sidebar from "../components/Sidebar/Sidebar";
import TopBar from "../components/TopBar/TopBar";
import StatsCards from "../components/StatsCards/StatsCards";
import LiveMap from "../components/LiveMap/LiveMap";
import RecentIncidents from "../components/RecentIncidents/RecentIncidents";
import TrafficAnalytics from "../components/TrafficAnalytics/TrafficAnalytics";
import RoadHealth from "../components/RoadHealth/RoadHealth";
import AIAssistant from "../components/AIAssistant/AIAssistant";
import { useLiveData } from "../hooks/useLiveData";
import {
  fetchStats,
  fetchMapData,
  fetchRecentIncidents,
  fetchTrafficAnalytics,
  fetchRoadHealth,
} from "../services/api";
import { mockAssistantPrompts } from "../data/mockData";
import "./Dashboard.css";

export default function Dashboard() {
  const [activeNav, setActiveNav] = useState("dashboard");
  const [trafficRange, setTrafficRange] = useState("24H");

  // Polling intervals simulate real-time updates. Swap these for a
  // WebSocket subscription once the backend supports push - see
  // hooks/useLiveData.js.
  const { data: stats, loading: statsLoading } = useLiveData(fetchStats, 15000);
  const { data: mapData, loading: mapLoading } = useLiveData(fetchMapData, 10000);
  const { data: incidents, loading: incidentsLoading } = useLiveData(
    () => fetchRecentIncidents(6),
    12000
  );
  const { data: trafficData, loading: trafficLoading } = useLiveData(
    () => fetchTrafficAnalytics(trafficRange),
    null,
    [trafficRange]
  );
  const { data: roadHealth, loading: roadHealthLoading } = useLiveData(fetchRoadHealth, 30000);

  return (
    <div className="dashboard-shell">
      <Sidebar activeItem={activeNav} onNavigate={setActiveNav} />

      <div className="dashboard-main">
        <TopBar notificationCount={3} />

        <div className="dashboard-content">
          <StatsCards stats={stats} loading={statsLoading} />

          <div className="dashboard-mid-row">
            <LiveMap
              markers={mapData?.markers}
              landmarks={mapData?.landmarks}
              loading={mapLoading}
            />
                        <RecentIncidents incidents={incidents || []} loading={incidentsLoading} />
          </div>

          <div className="dashboard-bottom-row">
            <TrafficAnalytics
              data={trafficData}
              range={trafficRange}
              onRangeChange={setTrafficRange}
              loading={trafficLoading}
            />
            <RoadHealth
              roads={roadHealth?.roads}
              totalSegments={roadHealth?.total_segments}
              loading={roadHealthLoading}
            />
          </div>
        </div>
      </div>

      <div className="dashboard-assistant-rail">
        <AIAssistant suggestedPrompts={mockAssistantPrompts} />
      </div>
    </div>
  );
}
