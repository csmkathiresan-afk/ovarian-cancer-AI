import { useEffect, useState } from "react";
import { getDevices, getIoTStatus } from "../api";
import DeviceStatus from "../components/DeviceStatus.jsx";

export default function IoTDevice() {
  const [iot, setIot] = useState(null);
  const [devices, setDevices] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const [status, list] = await Promise.all([getIoTStatus(), getDevices()]);
        setIot(status.data);
        setDevices(list.data.devices || []);
      } catch {
        setIot({ status: "offline", device_id: "ESP32_001" });
      }
    };
    load();
    const timer = setInterval(load, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div>
      <div className="header">
        <h2>IoT Device Monitor</h2>
        <p>ESP32 nodes register themselves and heartbeat while firmware is running.</p>
      </div>
      <DeviceStatus iot={iot} />
      <div className="card" style={{ marginTop: 16 }}>
        <h3>REGISTERED DEVICES</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Device ID</th>
                <th>Name</th>
                <th>IP Address</th>
                <th>Wi-Fi</th>
                <th>Status</th>
                <th>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {devices.length === 0 && <tr><td colSpan={6}>No ESP32 registered yet.</td></tr>}
              {devices.map((d) => (
                <tr key={d.device_id}>
                  <td>{d.device_id}</td>
                  <td>{d.device_name}</td>
                  <td>{d.ip_address || "—"}</td>
                  <td>{d.wifi_signal ?? "—"}</td>
                  <td>{d.status}</td>
                  <td>{d.last_seen ? new Date(d.last_seen).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
