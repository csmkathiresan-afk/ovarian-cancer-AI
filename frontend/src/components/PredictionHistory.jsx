import { useEffect, useState } from "react";
import { getPredictions } from "../api";

export default function PredictionHistory({ limit = 20 }) {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    getPredictions(limit)
      .then((res) => setRows(res.data.items || []))
      .catch(() => setRows([]));
  }, [limit]);

  return (
    <div className="card">
      <h3>RECENT PREDICTIONS</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Patient ID</th>
              <th>Prediction</th>
              <th>Probability</th>
              <th>Risk</th>
              <th>Device</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr><td colSpan={6}>No predictions stored yet.</td></tr>
            )}
            {rows.map((row) => (
              <tr key={row.id}>
                <td>{row.patient_id}</td>
                <td>{row.classification}</td>
                <td>{Math.round(row.probability * 100)}%</td>
                <td>{row.risk_level}</td>
                <td>{row.device_id || "—"}</td>
                <td>{row.timestamp ? new Date(row.timestamp).toLocaleString() : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
