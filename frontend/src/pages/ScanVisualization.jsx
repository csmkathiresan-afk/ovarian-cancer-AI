import { useState } from "react";

export default function ScanVisualization() {
  const [src, setSrc] = useState("/sample-scan.svg");

  const onFile = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setSrc(URL.createObjectURL(file));
  };

  return (
    <div>
      <div className="header">
        <h2>Reference Scan Visualization</h2>
        <p>Image shown for demonstration only. Current AI prediction uses clinical metadata.</p>
      </div>
      <div className="card">
        <h3>REFERENCE SCAN</h3>
        <p>The current project does NOT perform image-based cancer prediction.</p>
        <input type="file" accept="image/*" onChange={onFile} />
        <div className="scan-frame" style={{ marginTop: 16 }}>
          <img src={src} alt="Reference ovarian scan visualization" />
        </div>
        <p className="disclaimer">
          AI-generated risk assessment for academic/research demonstration.
          This system does not replace professional medical diagnosis.
        </p>
      </div>
    </div>
  );
}
