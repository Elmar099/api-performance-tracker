import subprocess
import json

def run_k6_test(vus, duration):
    result = subprocess.run(
    [
        "k6",
        "run",
        "--summary-export=k6/summary.json",
        "k6/test.js"
    ],
    capture_output=True,
    text=True,

    env={
        **__import__("os").environ,
        "K6_VUS": str(vus),
        "K6_DURATION": duration,
    }
)
    with open("k6/summary.json", "r") as file:
        summary = json.load(file)
    
    

    metrics = summary["metrics"]

    return {
        "success": result.returncode == 0,
        "requests": metrics["http_reqs"]["count"],
        "requests_per_second": metrics["http_reqs"]["rate"],
        "avg_latency_ms": metrics["http_req_duration"]["avg"],
        "p95_latency_ms": metrics["http_req_duration"]["p(95)"],
        "max_latency_ms": metrics["http_req_duration"]["max"],
        "failure_rate": metrics["http_req_failed"]["value"],
    }