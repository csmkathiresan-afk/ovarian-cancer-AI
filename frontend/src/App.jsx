import { NavLink, Route, Routes } from "react-router-dom";
import {
  Activity,
  Cpu,
  History,
  Home,
  Image,
  Info,
  Menu,
  Settings as SettingsIcon,
  Stethoscope,
  Workflow,
} from "lucide-react";
import { useState } from "react";
import Dashboard from "./pages/Dashboard.jsx";
import Prediction from "./pages/Prediction.jsx";
import IoTDevice from "./pages/IoTDevice.jsx";
import HistoryPage from "./pages/History.jsx";
import AnalyticsPage from "./pages/Analytics.jsx";
import ModelInfo from "./pages/ModelInfo.jsx";
import ScanVisualization from "./pages/ScanVisualization.jsx";
import Settings from "./pages/Settings.jsx";
import Wiring from "./pages/Wiring.jsx";

const links = [
  { to: "/", label: "Dashboard", icon: Home },
  { to: "/assessment", label: "Patient Assessment", icon: Stethoscope },
  { to: "/iot", label: "IoT Device", icon: Cpu },
  { to: "/history", label: "Prediction History", icon: History },
  { to: "/analytics", label: "Analytics", icon: Activity },
  { to: "/model", label: "AI Model", icon: Info },
  { to: "/scan", label: "Scan Visualization", icon: Image },
  { to: "/wiring", label: "Hardware Wiring", icon: Workflow },
  { to: "/settings", label: "Settings", icon: SettingsIcon },
];

export default function App() {
  const [open, setOpen] = useState(false);

  return (
    <div className="app-shell">
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="brand">
          <h1>OVARIAN CANCER AI</h1>
          <p>Smart IoT Clinical Risk Assessment Platform</p>
        </div>
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
            onClick={() => setOpen(false)}
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </aside>
      <main className="content">
        <button className="btn secondary menu-btn" onClick={() => setOpen((v) => !v)}>
          <Menu size={16} /> Menu
        </button>
        <div className="banner">Prototype for Research & Demonstration – Not for Clinical Diagnosis</div>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/assessment" element={<Prediction />} />
          <Route path="/iot" element={<IoTDevice />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/model" element={<ModelInfo />} />
          <Route path="/scan" element={<ScanVisualization />} />
          <Route path="/wiring" element={<Wiring />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}
