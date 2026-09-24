import { useEffect, useState } from "react";
import { getModelInfo } from "../api";

export default function ModelInfo() {
  const [info, setInfo] = useState(null);

  useEffect(() => {
    getModelInfo().then((res) => setInfo(res.data)).catch(() => setInfo(null));
  }, []);

  const metrics = info?.metrics;

  return (
    <div>
      <div className="header">
        <h2>AI Model</h2>
        <p>Metadata DNN loaded at backend startup. Predictions never retrain the network.</p>
      </div>
      <div className="grid grid-2">
        <div className="card">
          <h3>ARCHITECTURE</h3>
          <p>Model: Deep Neural Network</p>
          <p>Framework: TensorFlow / Keras</p>
          <p>Input Features: 9</p>
          <p>Output: Binary Classification</p>
          <p>Layers:</p>
          <ul>
            <li>64 neurons</li>
            <li>32 neurons</li>
            <li>16 neurons</li>
            <li>Sigmoid Output</li>
          </ul>
          <p>Training epochs: 50</p>
          <p>Optimizer: Adam</p>
          <p>Loss: Binary Crossentropy</p>
        </div>
        <div className="card">
          <h3>EVALUATION METRICS</h3>
          {metrics?.available ? (
            <>
              <p>Accuracy: {metrics.accuracy?.toFixed(4)}</p>
              <p>Precision: {metrics.precision?.toFixed(4)}</p>
              <p>Recall: {metrics.recall?.toFixed(4)}</p>
              <p>F1 Score: {metrics.f1?.toFixed(4)}</p>
              <p className="disclaimer">{metrics.note}</p>
              <p className="disclaimer">Dataset: {metrics.dataset}</p>
            </>
          ) : (
            <p>No saved evaluation metrics were found with the trained model. Values are not invented.</p>
          )}
        </div>
      </div>
      <p className="disclaimer">{info?.disclaimer}</p>
    </div>
  );
}
