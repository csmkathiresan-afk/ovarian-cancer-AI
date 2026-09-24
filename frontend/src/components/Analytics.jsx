import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const COLORS = ["#3ee0a3", "#ff6b7d", "#f5c542", "#3ec8ff"];

export default function Analytics({ data }) {
  if (!data) return <div className="card">Loading analytics…</div>;

  const classData = Object.entries(data.prediction_distribution || {}).map(([name, value]) => ({ name, value }));
  const riskData = Object.entries(data.risk_distribution || {}).map(([name, value]) => ({ name, value }));

  return (
    <div className="grid grid-2">
      <div className="card">
        <h3>PREDICTION DISTRIBUTION</h3>
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie data={classData} dataKey="value" nameKey="name" outerRadius={80} label>
              {classData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="card">
        <h3>RISK DISTRIBUTION</h3>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={riskData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1d334d" />
            <XAxis dataKey="name" stroke="#8aa4bf" />
            <YAxis stroke="#8aa4bf" />
            <Tooltip />
            <Bar dataKey="value" fill="#3ec8ff" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="card">
        <h3>PREDICTION HISTORY</h3>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={data.history || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1d334d" />
            <XAxis dataKey="timestamp" hide />
            <YAxis domain={[0, 1]} stroke="#8aa4bf" />
            <Tooltip />
            <Line type="monotone" dataKey="probability" stroke="#4f8cff" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="card">
        <h3>CA125 VS PROBABILITY</h3>
        <ResponsiveContainer width="100%" height={240}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#1d334d" />
            <XAxis dataKey="ca125" name="CA125" stroke="#8aa4bf" />
            <YAxis dataKey="probability" name="Probability" domain={[0, 1]} stroke="#8aa4bf" />
            <Tooltip />
            <Scatter data={data.ca125_vs_probability || []} fill="#3ee0a3" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <div className="card">
        <h3>TUMOR SIZE VS PROBABILITY</h3>
        <ResponsiveContainer width="100%" height={240}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#1d334d" />
            <XAxis dataKey="tumor_size" name="Tumor size" stroke="#8aa4bf" />
            <YAxis dataKey="probability" name="Probability" domain={[0, 1]} stroke="#8aa4bf" />
            <Tooltip />
            <Scatter data={data.tumor_size_vs_probability || []} fill="#f5c542" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <div className="card">
        <h3>DAILY PREDICTION COUNT</h3>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={data.daily_counts || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1d334d" />
            <XAxis dataKey="date" stroke="#8aa4bf" />
            <YAxis stroke="#8aa4bf" />
            <Tooltip />
            <Bar dataKey="count" fill="#4f8cff" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="card">
        <h3>DEVICE ACTIVITY</h3>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={data.device_activity || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1d334d" />
            <XAxis dataKey="device_id" stroke="#8aa4bf" />
            <YAxis stroke="#8aa4bf" />
            <Tooltip />
            <Bar dataKey="count" fill="#ff6b7d" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
