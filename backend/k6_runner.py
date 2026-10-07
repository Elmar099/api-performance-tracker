import subprocess
import json
import os
from urllib.parse import urlparse, urlunparse


def get_docker_url(url):
    parsed = urlparse(url)

    if parsed.hostname in {"127.0.0.1", "localhost"}:
        hostname = "host.docker.internal"

        if parsed.port:
            netloc = f"{hostname}:{parsed.port}"
        else:
            netloc = hostname

        parsed = parsed._replace(netloc=netloc)

    return urlunparse(parsed)


def run_k6_test(url, vus, duration, p95_threshold_ms):
    summary_dir = os.path.abspath("k6")
    summary_path = os.path.join(summary_dir, "summary.json")

    if os.path.exists(summary_path):
        os.remove(summary_path)

    docker_url = get_docker_url(url)

    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-e",
            f"K6_VUS={vus}",
            "-e",
            f"K6_DURATION={duration}",
            "-e",
            f"K6_URL={docker_url}",
            "-e",
            f"K6_P95_THRESHOLD={p95_threshold_ms}",
            "-v",
            f"{summary_dir}:/tmp",
            "api-performance-k6",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
            or result.stdout.strip()
            or "Docker k6 test failed"
        )

    with open(summary_path, "r") as file:
        summary = json.load(file)

    metrics = summary["metrics"]

    return {
        "threshold_passed": result.returncode == 0,
        "requests": metrics["http_reqs"]["count"],
        "requests_per_second": metrics["http_reqs"]["rate"],
        "avg_latency_ms": metrics["http_req_duration"]["avg"],
        "p95_latency_ms": metrics["http_req_duration"]["p(95)"],
        "max_latency_ms": metrics["http_req_duration"]["max"],
        "failure_rate": metrics["http_req_failed"]["value"],
    }