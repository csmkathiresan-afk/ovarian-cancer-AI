export default function PatientForm({ form, setForm, onSubmit, busy, onDemo, onSendEsp }) {
  const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));
  const yesNo = (key) => (
    <select value={form[key]} onChange={(e) => set(key, Number(e.target.value))}>
      <option value={0}>No</option>
      <option value={1}>Yes</option>
    </select>
  );

  return (
    <form className="card" onSubmit={onSubmit}>
      <h3>CLINICAL METADATA</h3>
      <div className="form-grid">
        <label>Patient ID<input value={form.patient_id} onChange={(e) => set("patient_id", e.target.value)} required /></label>
        <label>Age<input type="number" min="1" max="120" value={form.age} onChange={(e) => set("age", Number(e.target.value))} required /></label>
        <label>CA125<input type="number" min="0" step="0.1" value={form.ca125} onChange={(e) => set("ca125", Number(e.target.value))} required /></label>
        <label>Tumor Size<input type="number" min="0" step="0.1" value={form.tumor_size} onChange={(e) => set("tumor_size", Number(e.target.value))} required /></label>
        <label>Menopause{yesNo("menopause")}</label>
        <label>Family History{yesNo("family_history")}</label>
        <label>Ascites{yesNo("ascites")}</label>
        <label>Bilateral{yesNo("bilateral")}</label>
        <label>Solid Component{yesNo("solid_component")}</label>
        <label>Septation{yesNo("septation")}</label>
      </div>
      <div className="actions">
        <button className="btn" disabled={busy} type="submit">{busy ? "Analyzing..." : "ANALYZE PATIENT"}</button>
        <button className="btn secondary" type="button" onClick={() => onDemo("A")}>DEMO A · Low</button>
        <button className="btn secondary" type="button" onClick={() => onDemo("B")}>DEMO B · Medium</button>
        <button className="btn secondary" type="button" onClick={() => onDemo("C")}>DEMO C · High</button>
        <button className="btn secondary" type="button" onClick={onSendEsp}>Send to ESP32</button>
      </div>
    </form>
  );
}
