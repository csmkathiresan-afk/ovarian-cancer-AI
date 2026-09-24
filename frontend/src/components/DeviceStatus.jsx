function bars(rssi) {
  if (rssi == null) return "░░░░░░░░░░";
  const quality = Math.max(0, Math.min(10, Math.round((rssi + 90) / 5)));
  return `${"█".repeat(quality)}${"░".repeat(10 - quality)}`;
}

function ago(iso) {
  if (!iso) return "never";
  const ms = Date.now() - new Date(iso).getTime();
  const sec = Math.max(0, Math.round(ms / 1000));
  if (sec < 60) return `${sec} seconds ago`;
  return `${Math.round(sec / 60)} minutes ago`;
}

export default function DeviceStatus({ iot }) {
  const online = iot?.status === "online";
  return (
    <div className="card">
      <h3>ESP32 DEVICE</h3>
      <p className="metric">{online ? "● ONLINE" : "● OFFLINE"}</p>
      <p>Device: {iot?.device_id || "ESP32_001"}</p>
      <p>Wi-Fi Signal <span className="signal">{bars(iot?.wifi_signal)}</span></p>
      <p>Last Prediction {iot?.last_prediction ? `${iot.last_prediction} RISK` : "—"}</p>
      <p>Last Communication {ago(iot?.last_seen)}</p>
    </div>
  );
}
