# Skill: Load & Performance Testing (k6)

## Purpose
To evaluate how a system performs under stress and high traffic, ensuring it can handle expected and peak loads without degrading performance or crashing. [k6](https://k6.io/) by Grafana is a modern, developer-centric load testing tool written in Go, using JavaScript for test scripts.

## When to Use
- Before launching a new service or major feature that expects high traffic
- When validating autoscaling configurations (e.g., Kubernetes HPA or AWS Auto Scaling)
- When establishing performance baselines (SLAs/SLOs) for API response times
- When identifying bottlenecks in the database, network, or application code

## Procedure

### 1. Installation
Install k6 locally based on your OS.
- **macOS**: `brew install k6`
- **Linux**: `sudo apt-get install k6`
- **Windows**: `winget install k6`

### 2. Writing the Test Script
Create a JavaScript file (e.g., `load-test.js`) defining the test logic, user behavior, and thresholds.

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

// 1. Configuration (Options)
export const options = {
  // Define stages for ramping up and down virtual users (VUs)
  stages: [
    { duration: '30s', target: 50 },  // Ramp-up to 50 users over 30 seconds
    { duration: '1m', target: 50 },   // Stay at 50 users for 1 minute
    { duration: '30s', target: 0 },   // Ramp-down to 0 users over 30 seconds
  ],
  
  // Define Service Level Objectives (SLOs) as thresholds
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
    http_req_failed: ['rate<0.01'],   // Error rate must be less than 1%
  },
};

// 2. Setup (Optional) - Runs once before the test starts
export function setup() {
  // e.g., Authenticate and return a token to be used by all VUs
  const res = http.post('https://api.example.com/login', {
    user: 'admin', password: 'password123'
  });
  return { token: res.json('token') };
}

// 3. VU Logic (The default function) - Runs repeatedly per VU
export default function (data) {
  const headers = { 'Authorization': `Bearer ${data.token}` };
  
  // Make a GET request
  const res = http.get('https://api.example.com/products', { headers });
  
  // Assertions (Checks do not fail the test immediately like thresholds do)
  check(res, {
    'status is 200': (r) => r.status === 200,
    'transaction time OK': (r) => r.timings.duration < 200,
  });
  
  // Simulate user think time
  sleep(1);
}

// 4. Teardown (Optional) - Runs once after the test finishes
export function teardown(data) {
  // Clean up test data if necessary
}
```

### 3. Running the Test
Execute the script from the terminal:
```bash
k6 run load-test.js
```

To output results to a JSON or CSV file for further analysis:
```bash
k6 run --out json=results.json load-test.js
```

## Best Practices
- **Do NOT Load Test Production**: Unless specifically planned and coordinated with the infrastructure/DevOps team. Test in a dedicated staging or pre-production environment that mirrors production architecture.
- **Use Realistic User Journeys**: Don't just hammer a single endpoint. Simulate real user behavior (e.g., login -> browse -> add to cart -> checkout) using randomized think times (`sleep()`).
- **Monitor the Backend**: Load testing is useless if you don't monitor the system under test. Watch CPU, Memory, DB connections, and network I/O during the test using tools like Datadog, New Relic, or Prometheus.