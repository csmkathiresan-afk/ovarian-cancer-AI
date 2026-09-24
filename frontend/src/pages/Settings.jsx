import { useEffect, useState } from "react";
import { getSettings } from "../api";

export default function Settings() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getSettings().then((res) => setData(res.data)).catch(() => setData(null));
  }, []);

  return (
    <div>
      <div className="header">
        <h2>Settings</h2>
        <p>Risk cutoffs live in backend environment variables. They are not model weights.</p>
      </div>
      <div className="card">
        <h3>PROTOTYPE RISK THRESHOLDS</h3>
        <p>Low if probability &lt; {data?.risk_low_threshold ?? "0.30"}</p>
        <p>Medium between low and high</p>
        <p>High if probability &gt; {data?.risk_high_threshold ?? "0.70"}</p>
        <p className="disclaimer">{data?.note}</p>
        <p className="disclaimer">Edit RISK_LOW_THRESHOLD and RISK_HIGH_THRESHOLD in backend/.env and restart the API.</p>
      </div>
    </div>
  );
}
