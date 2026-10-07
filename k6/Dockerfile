FROM grafana/k6:latest

COPY test.js /test.js

ENTRYPOINT ["k6", "run", "--summary-export=/tmp/summary.json", "/test.js"]