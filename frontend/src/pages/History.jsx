import PredictionHistory from "../components/PredictionHistory.jsx";

export default function History() {
  return (
    <div>
      <div className="header">
        <h2>Prediction History</h2>
        <p>SQLite-backed research log of metadata risk assessments.</p>
      </div>
      <PredictionHistory limit={100} />
    </div>
  );
}
