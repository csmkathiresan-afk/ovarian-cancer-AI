import { useEffect, useState } from "react";
import { getAnalytics } from "../api";
import Analytics from "../components/Analytics.jsx";

export default function AnalyticsPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getAnalytics().then((res) => setData(res.data)).catch(() => setData({}));
  }, []);

  return (
    <div>
      <div className="header">
        <h2>Analytics</h2>
        <p>Prototype dashboards over stored assessments. Not clinical quality measures.</p>
      </div>
      <Analytics data={data} />
    </div>
  );
}
