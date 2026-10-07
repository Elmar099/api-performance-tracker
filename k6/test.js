import http from "k6/http";
import { check } from "k6";

export const options = {
    vus: __ENV.K6_VUS,
    duration: __ENV.K6_DURATION,

    thresholds: {
        http_req_duration: [`p(95)<${__ENV.K6_P95_THRESHOLD}`],
    },
};

export default function () {
    const response = http.get(__ENV.K6_URL);

    check(response, {
        "status is 200": (r) => r.status === 200,
    });
}