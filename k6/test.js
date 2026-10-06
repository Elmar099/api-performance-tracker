import http from "k6/http";
import { check } from "k6";

export const options = {
    vus: __ENV.K6_VUS,
    duration: __ENV.K6_DURATION,

    thresholds: {
        http_req_duration: ["p(95)<50"],
    },
};

export default function () {
    const response = http.get("http://127.0.0.1:8000/api/users");

    check(response, {
        "status is 200": (r) => r.status === 200,
    });
}