import { useEffect, useState } from "react";

function App() {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  return (
    <div>
      <h1>API Performance Tracker</h1>

      <h2>Test History</h2>

      {loading && <p>Loading tests...</p>}

      {error && <p>Error: {error}</p>}

      {tests.map((test) => (
        <div key={test.id}>
          <p>URL: {test.url}</p>
          <p>Requests: {test.requests}</p>
          <p>Requests/sec: {test.requests_per_second}</p>
          <p>Average latency: {test.avg_latency_ms} ms</p>
          <p>P95 latency: {test.p95_latency_ms} ms</p>
        </div>
      ))}
    </div>
  );
}

export default App;