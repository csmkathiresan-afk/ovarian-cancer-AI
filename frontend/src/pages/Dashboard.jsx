import { useEffect, useState } from "react";
import { getAnalytics, getHealth, getIoTStatus } from "../api";
import DeviceStatus from "../components/DeviceStatus.jsx";
import PredictionHistory from "../components/PredictionHistory.jsx";

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [iot, setIot] = useState(null);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [h, i, a] = await Promise.all([getHealth(), getIoTStatus(), getAnalytics()]);
        setHealth(h.data);
        setIot(i.data);
        setAnalytics(a.data);
      } catch {
        setHealth({ api: "offline", model_loaded: false });
      }
    };
    load();
    const timer = setInterval(load, 8000);
    return () => clearInterval(timer);
  }, []);

  const apiOnline = health?.api === "online";
  const modelOnline = Boolean(health?.model_loaded);
  const espOnline = iot?.status === "online";

  return (
    <div>
      <div className="header">
        <h2>OVARIAN CANCER AI</h2>
        <p>Smart IoT Clinical Risk Assessment Platform</p>
      </div>
      <div className="status-pills">
        <span className="pill"><span className={`dot ${modelOnline ? "on" : "off"}`} /> AI Model Status: {modelOnline ? "ONLINE" : "OFFLINE"}</span>
        <span className="pill"><span className={`dot ${espOnline ? "on" : "off"}`} /> ESP32 Status: {espOnline ? "CONNECTED" : "DISCONNECTED"}</span>
        <span className="pill"><span className={`dot ${apiOnline ? "on" : "off"}`} /> API Status: {apiOnline ? "ONLINE" : "OFFLINE"}</span>
      </div>
      <div className="grid grid-4">
        <div className="card">
          <h3>AI MODEL</h3>
          <p className="metric">{modelOnline ? "● ONLINE" : "● OFFLINE"}</p>
        </div>
        <div className="card">
          <h3>ESP32 DEVICE</h3>
          <p className="metric">{espOnline ? "● CONNECTED" : "● DISCONNECTED"}</p>
        </div>
        <div className="card">
          <h3>PATIENTS</h3>
          <p className="metric">{analytics?.totals?.patients ?? 0}</p>
        </div>
        <div className="card">
          <h3>PREDICTIONS</h3>
          <p className="metric">{analytics?.totals?.predictions ?? 0}</p>
        </div>
      </div>
      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <DeviceStatus iot={iot} />
        <div className="card result-hero">
          <h3>AI RISK ASSESSMENT</h3>
          <p className="risk MEDIUM">Awaiting analysis</p>
          <p>Submit clinical metadata on Patient Assessment to generate a research risk score.</p>
          <p className="disclaimer">Clinical Review Needed for any concerning result. This is not a diagnosis.</p>
        </div>
      </div>
      <div style={{ marginTop: 16 }}>
        <PredictionHistory limit={8} />
      </div>
    </div>
  );
}
