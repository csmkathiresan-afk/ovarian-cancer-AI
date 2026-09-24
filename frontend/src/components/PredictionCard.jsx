export default function PredictionCard({ result, message }) {
  if (!result) {
    return (
      <div className="card result-hero">
        <h3>AI PREDICTION</h3>
        <p className="risk MEDIUM">No result yet</p>
        <p>Complete the form and choose ANALYZE PATIENT.</p>
        {message && <p className="disclaimer">{message}</p>}
      </div>
    );
  }

  const code = result.risk_level?.toUpperCase().includes("HIGH")
    ? "HIGH"
    : result.risk_level?.toUpperCase().includes("MEDIUM")
      ? "MEDIUM"
      : "LOW";
  const pct = Math.round((result.probability || 0) * 100);

  return (
    <div className="card result-hero">
      <h3>AI RISK ASSESSMENT</h3>
      <p className={`risk ${code}`}>{result.risk_level}</p>
      <p>Probability: {pct}%</p>
      <p>Classification: {result.classification}</p>
      <p>Patient ID: {result.patient_id}</p>
      <p>Timestamp: {new Date(result.timestamp).toLocaleString()}</p>
      <p>Clinical Review Needed</p>
      {message && <p>{message}</p>}
      <p className="disclaimer">
        High-risk / low-risk language is a prototype presentation layer.
        This is not a diagnosis and must not be read as “cancer confirmed”.
      </p>
    </div>
  );
}
