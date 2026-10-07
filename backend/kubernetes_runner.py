import json
import time
from kubernetes import client, config
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

def create_k6_job(test_id, url, vus, duration, p95_threshold_ms, method):
    config.load_kube_config()

    batch_api = client.BatchV1Api()

    job = client.V1Job(
        metadata=client.V1ObjectMeta(
            name=f"k6-{test_id[:8]}"
        ),
        spec=client.V1JobSpec(
            backoff_limit=0,
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    restart_policy="Never",
                    containers=[
                        client.V1Container(
                            name="k6",
                            image="api-performance-k6:latest",
                            env=[
                                client.V1EnvVar(
                                    name="K6_VUS",
                                    value=str(vus)
                                ),
                                client.V1EnvVar(
                                    name="K6_DURATION",
                                    value=duration
                                ),
                                client.V1EnvVar(
                                    name="K6_URL",
                                    value=get_docker_url(url)
                                ),
                                client.V1EnvVar(
                                    name="K6_P95_THRESHOLD",
                                    value=str(p95_threshold_ms)
                                ),
                                client.V1EnvVar(
                                    name="K6_METHOD",
                                    value=method
                                ),
                                client.V1EnvVar(
                                    name="K6_PROMETHEUS_RW_SERVER_URL",
                                    value="http://prometheus:9090/api/v1/write"
                                ),
                                client.V1EnvVar(
                                    name="K6_PROMETHEUS_RW_PUSH_INTERVAL",
                                    value="1s"
                                ),
                                client.V1EnvVar(
                                    name="K6_PROMETHEUS_RW_TREND_AS_NATIVE_HISTOGRAM",
                                    value="true"
                                ),
                            ],
                            command=[
                                "k6",
                                "run",
                                "--out",
                                "experimental-prometheus-rw",
                                "/test.js",
                            ],
                        )
                    ],
                )
            ),
        ),
    )

    return batch_api.create_namespaced_job(
        namespace="default",
        body=job
    )

def get_k6_results(job_name):
    config.load_kube_config()

    core_api = client.CoreV1Api()

    pods = core_api.list_namespaced_pod(
        namespace="default",
        label_selector=f"job-name={job_name}"
    )

    if not pods.items:
        raise RuntimeError("No pod found for Kubernetes Job")

    pod_name = pods.items[0].metadata.name

    logs = core_api.read_namespaced_pod_log(
        name=pod_name,
        namespace="default"
    )

    for line in reversed(logs.splitlines()):
        line = line.strip()

        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)

    raise RuntimeError("k6 JSON summary not found in pod logs")


def run_kubernetes_test(test_id, url, vus, duration, p95_threshold_ms, method):
    job = create_k6_job(
        test_id,
        url,
        vus,
        duration,
        p95_threshold_ms,
        method
    )

    job_name = job.metadata.name

    config.load_kube_config()

    batch_api = client.BatchV1Api()

    while True:
        current_job = batch_api.read_namespaced_job(
            name=job_name,
            namespace="default"
        )

        status = current_job.status

        if status.succeeded:
            return get_k6_results(job_name)

        if status.failed:
            raise RuntimeError("Kubernetes k6 Job failed")

        time.sleep(1)