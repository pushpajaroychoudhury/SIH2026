import { Search, Bell, ChevronDown } from "lucide-react";
import "./TopBar.css";

export default function TopBar({ notificationCount = 3 }) {
  return (
    <header className="topbar">
      <div className="topbar-status">
        <span className="status-dot" />
        <span>System Online</span>
      </div>

      <div className="topbar-search">
        <Search size={16} />
        <input placeholder="Search incidents, routes, or locations..." />
      </div>

      <div className="topbar-actions">
        <button className="topbar-icon-btn" aria-label="Notifications">
          <Bell size={18} />
          {notificationCount > 0 && (
            <span className="notif-dot">{notificationCount}</span>
          )}
        </button>

        <div className="topbar-profile">
          <div className="topbar-avatar">A</div>
          <div className="topbar-profile-text">
            <div className="topbar-profile-name">Admin</div>
            <div className="topbar-profile-role">City Authority</div>
          </div>
          <ChevronDown size={16} />
        </div>
      </div>
    </header>
  );
}
