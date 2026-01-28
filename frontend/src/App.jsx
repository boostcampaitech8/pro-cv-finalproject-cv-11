import { useState } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

function App() {
  const [connectStatus, setConnectStatus] = useState(null);
  const [connectError, setConnectError] = useState(null);
  const [dbStatus, setDbStatus] = useState(null);
  const [dbError, setDbError] = useState(null);

  const connectCheck = async () => {
    setConnectStatus(null);
    setConnectError(null);
    try {
      const res = await fetch(`${API}/v1/connect_check`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setConnectStatus(data.detail || "ok");
    } catch (err) {
      setConnectError(err.message);
    }
  };

  const dbCheck = async () => {
    setDbStatus(null);
    setDbError(null);
    try {
      const res = await fetch(`${API}/v1/db_check`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
      setDbStatus(data.detail || "db ok");
    } catch (err) {
      setDbError(err.message);
    }
  };

  return (
    <main className="app">
      <header>
        <p className="eyebrow">Connectivity</p>
        <h1>FE ↔ BE ↔ DB 체크</h1>
        <p className="muted">
          API base: <code>{API}</code>
        </p>
      </header>

      <section className="card">
        <div className="card-head">
          <h2>Connection Checks</h2>
          <div className="actions">
            <button onClick={connectCheck}>FE → BE</button>
            <button onClick={dbCheck} className="secondary">
              BE → DB
            </button>
          </div>
        </div>
        {connectStatus && <p className="ok">Backend: {connectStatus}</p>}
        {connectError && <p className="fail">Backend error: {connectError}</p>}
        {dbStatus && <p className="ok">Database: {dbStatus}</p>}
        {dbError && <p className="fail">Database error: {dbError}</p>}
      </section>
    </main>
  );
}

export default App;
