import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [url, setUrl] = useState("");
  const [vus, setVus] = useState(1);
  const [duration, setDuration] = useState("5s");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/api/tests`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch tests");
        }

        return response.json();
      })
      .then((data) => setTests(data))
      .catch((error) => setError(error.message))
      .finally(() => setLoading(false));
  }, []);

  const runTest = async (event) => {
  event.preventDefault();

  setRunning(true);
  setResult(null);

  try {
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/tests`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url,
          vus,
          duration,
        }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to run test");
    }

    const data = await response.json();

    setResult(data);

    const historyResponse = await fetch(
    `${import.meta.env.VITE_API_URL}/api/tests`
    );

    const historyData = await historyResponse.json();

    setTests(historyData);

  } catch (error) {
    console.error(error);
  } finally {
    setRunning(false);
  }
};

  return (
    <div>
      <h1>API Performance Tracker</h1>

      <h2>Run Performance Test</h2>

    <form onSubmit={runTest}>
      <div>
        <label>API URL</label>
        <input
          type="text"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="http://127.0.0.1:8000/api/users"
        />
      </div>

  <div>
    <label>Virtual Users</label>
    <input
      type="number"
      value={vus}
      onChange={(event) => setVus(Number(event.target.value))}
      min="1"
      max="1000"
    />
  </div>

  <div>
    <label>Duration</label>
    <input
      type="text"
      value={duration}
      onChange={(event) => setDuration(event.target.value)}
      placeholder="10s"
    />
  </div>

  <button type="submit" disabled={running}>
  {running ? "Running Test..." : "Run Test"}
  </button>
</form>
      {result && (
  <div className="latest-result">
    <h2>Latest Test Result</h2>

    <div className="test-info">
      <p><strong>URL:</strong> {result.config.url}</p>
      <p><strong>Virtual Users:</strong> {result.config.vus}</p>
      <p><strong>Duration:</strong> {result.config.duration}</p>
    </div>

    <div className="metrics">
      <div className="metric-card">
        <span>Requests</span>
        <strong>{result.results.requests}</strong>
      </div>

      <div className="metric-card">
        <span>Requests/sec</span>
        <strong>{result.results.requests_per_second.toFixed(2)}</strong>
      </div>

      <div className="metric-card">
        <span>Avg Latency</span>
        <strong>
          {result.results.avg_latency_ms.toFixed(2)} ms
        </strong>
      </div>

      <div className="metric-card">
        <span>P95 Latency</span>
        <strong>
          {result.results.p95_latency_ms.toFixed(2)} ms
        </strong>
      </div>

      <div className="metric-card">
        <span>Max Latency</span>
        <strong>
          {result.results.max_latency_ms.toFixed(2)} ms
        </strong>
      </div>

      <div className="metric-card">
        <span>Failure Rate</span>
        <strong>
          {(result.results.failure_rate * 100).toFixed(2)}%
        </strong>
      </div>
    </div>
  </div>
)}
      <h2>Test History</h2>

      {loading && <p>Loading tests...</p>}

      {error && <p>Error: {error}</p>}

      {!loading && !error && tests.length === 0 && (
        <p>No tests have been run yet.</p>
      )}

      {!loading && !error && tests.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>URL</th>
              <th>VUs</th>
              <th>Duration</th>
              <th>Requests</th>
              <th>Req/sec</th>
              <th>Avg Latency</th>
              <th>P95 Latency</th>
              <th>Max Latency</th>
              <th>Failure Rate</th>
            </tr>
          </thead>

          <tbody>
            {tests.map((test) => (
              <tr key={test.id}>
                <td>{test.url}</td>
                <td>{test.vus}</td>
                <td>{test.duration}</td>
                <td>{test.requests}</td>
                <td>{test.requests_per_second.toFixed(2)}</td>
                <td>{test.avg_latency_ms.toFixed(2)} ms</td>
                <td>{test.p95_latency_ms.toFixed(2)} ms</td>
                <td>{test.max_latency_ms.toFixed(2)} ms</td>
                <td>{(test.failure_rate * 100).toFixed(2)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;