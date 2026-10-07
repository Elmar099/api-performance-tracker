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
    let response;

    switch (__ENV.K6_METHOD) {
        case "POST":
            response = http.post(__ENV.K6_URL);
            break;
    
        case "PUT":
            response = http.put(__ENV.K6_URL);
            break;
    
        case "DELETE":
            response = http.del(__ENV.K6_URL);
            break;
    
        default:
            response = http.get(__ENV.K6_URL);
    }

    check(response, {
        "status is 200": (r) => r.status === 200,
    });
}
export function handleSummary(data) {
    return {
        stdout: JSON.stringify(data),
    };
}