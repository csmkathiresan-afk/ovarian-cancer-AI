import { useState } from "react";
import PatientForm from "../components/PatientForm.jsx";
import PredictionCard from "../components/PredictionCard.jsx";
import { predict, pushToDevice } from "../api";

const demos = {
  A: {
    patient_id: "PATIENT-A",
    age: 32,
    ca125: 18,
    tumor_size: 2.1,
    menopause: 0,
    family_history: 0,
    ascites: 0,
    bilateral: 0,
    solid_component: 0,
    septation: 0,
  },
  B: {
    patient_id: "PATIENT-B",
    age: 48,
    ca125: 85,
    tumor_size: 6.0,
    menopause: 0,
    family_history: 1,
    ascites: 0,
    bilateral: 1,
    solid_component: 0,
    septation: 1,
  },
  C: {
    patient_id: "PATIENT-C",
    age: 62,
    ca125: 600,
    tumor_size: 11.5,
    menopause: 1,
    family_history: 1,
    ascites: 1,
    bilateral: 1,
    solid_component: 1,
    septation: 0,
  },
};

export default function Prediction() {
  const [form, setForm] = useState(demos.A);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  const analyze = async (event) => {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const res = await predict({ ...form, device_id: "WEB_DASHBOARD" });
      setResult(res.data);
    } catch (err) {
      setMessage(err.response?.data?.detail || "Prediction error. Check API and input values.");
    } finally {
      setBusy(false);
    }
  };

  const sendEsp = async () => {
    setBusy(true);
    try {
      await pushToDevice({ ...form, device_id: "ESP32_001" });
      setMessage("Queued for ESP32_001. The device will pick this up on its next poll.");
    } catch (err) {
      setMessage(err.response?.data?.detail || "ESP32 is not registered yet. Power the board and wait for heartbeat.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div className="header">
        <h2>Patient Assessment</h2>
        <p>Enter clinical metadata. The DNN uses these nine features only — not scan images.</p>
      </div>
      <div className="grid grid-2">
        <PatientForm
          form={form}
          setForm={setForm}
          onSubmit={analyze}
          busy={busy}
          onDemo={(key) => setForm(demos[key])}
          onSendEsp={sendEsp}
        />
        <PredictionCard result={result} message={message} />
      </div>
      <p className="disclaimer">
        AI-generated risk assessment for academic/research demonstration.
        This system does not replace professional medical diagnosis.
      </p>
    </div>
  );
}
