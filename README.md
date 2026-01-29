# SRE_Platform
### What is  build
- A simple web app (Python Flask)
- Prometheus for metrics
- Grafana for dashboards
- Everything running in Docker containers (Docker Compose)

Docker Role
- Each component runs in its own container
- You can kill containers intentionally to simulate failures
---
### SLI (Service Level Indicator)
- Availability
```
successful_requests / total_requests
```
- Measured using Prometheus metrics

SLIs are **measurable metrics** that indicate how well the service is performing.

| SLI Name                 | Definition                                 | Metric / Measurement                                   |
|---------------------------|--------------------------------------------|-------------------------------------------------------|
| Request success rate      | % of requests that return HTTP 200         | `http_requests_total{status="200"}` vs total requests |
| Request latency           | How long a request takes                   | `http_request_latency_seconds` histogram             |
| Error rate                | % of requests resulting in HTTP 500       | `http_requests_total{status="500"}`                  |
| Resume parsing accuracy   | % of resumes where skill extraction matches JD (optional) | Custom metric: `resume_matching_score`              |

**Example SLIs:**

- **SLI1:** Successful requests = 95% of all requests  
- **SLI2:** 95th percentile request latency < 2s  
---

### SLO (Service Level Objective)

SLOs are **target goals** based on your SLIs. They are **internal targets**.

| SLO Name                  | Target                               | Measurement                                                                 |
|----------------------------|-------------------------------------|-----------------------------------------------------------------------------|
| Availability / Success Rate| 99% of requests return 200 OK        | `http_requests_total{status="200"} / total_requests`                        |
| Latency                    | 95% of requests < 2 seconds          | `histogram_quantile(0.95, sum(rate(http_request_latency_seconds_bucket[5m])) by (le))` |
| Error rate                 | Less than 1% of requests fail        | `http_requests_total{status="500"} / total_requests`                        |
| Resume parsing accuracy    | Average matching score ≥ 80%         | `avg(resume_matching_score)` (custom metric if implemented)                 |

**Example Interpretation:**

> If your SLO for availability is 99%, then out of 10,000 requests, up to 100 requests can fail without violating the SLO.  

Example:  
    “99.9% of HTTP requests must return a 2xx status over a 30-day window”

---

### SLA (Service Level Agreement)

SLAs are **formal agreements with users or stakeholders** that include **penalties or obligations** if SLOs are violated.

## Example SLA for Resume Parsing App

| SLA Metric      | Target / Commitment                     | Notes / Clauses                                                                 |
|-----------------|----------------------------------------|-------------------------------------------------------------------------------|
| Availability    | 99% uptime per month                     | If uptime < 99%, the provider must fix the service within 24h                 |
| Latency         | 95% of requests served in <2s           | If latency SLO is violated for >10% of requests in a month, report to stakeholders |
| Error Rate      | ≤1% failed requests per month           | Monitor and remediate errors proactively                                       |

---

**Explanation in SRE Context:**

- **SLI (Service Level Indicator):** Raw metric you track (e.g., `http_requests_total`, `http_request_latency_seconds`)  
- **SLO (Service Level Objective):** Internal target for your service (e.g., 99% availability, 95th percentile latency <2s)  
- **SLA (Service Level Agreement):** What your customers see, including obligations if the SLO is violated
  
Example:  
“If availability drops below 99.9%, users receive a 10% service credit”  

--- 

### Demo Moment
- Stop the app container
- Show Grafana dashboard dropping
- Explain how SLI affects SLO compliance

## Chaos Testing

Chaos engineering helps **validate the resilience** of the application under failures.

**Chaos Scenarios:**

- Simulate pod crashes or container restarts (`docker kill` or `kubectl delete pod`)  
- Introduce network latency or packet loss (using `tc` command)  
- Simulate high load (spike in HTTP requests)  

**Goal:** Ensure the service can **recover automatically** without violating SLOs.

---

### Auto-Healing

Auto-healing ensures **minimal downtime** by automatically recovering failed components.

**Strategies for this project:**

- **Container restart policies:** Always restart failed Docker containers
  ```yaml
  restart: unless-stopped