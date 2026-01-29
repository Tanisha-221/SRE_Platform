# SRE_Platform

# Resume Matching & Evaluation Platform (Local Deployment with SRE Monitoring and Automation)

## **Project Overview:**

The **Resume Matching & Evaluation Platform** is a web-based application designed to help **job seekers** and **hiring teams** evaluate resumes against job descriptions (JD) efficiently. This platform is optimized with **Prometheus** for monitoring, **Chaos Engineering** for resilience testing, and **Autohealing** features to maintain high availability. The system follows **Site Reliability Engineering (SRE)** principles to ensure high performance, reliability, and scalability in the recruitment process. This version of the platform is intended for **local deployment** and can be run on your local machine or a local server.

## **Key Features:**

1. **Resume Parsing & Skill Extraction:**
   - The platform supports **PDF** and **DOCX** resume formats.
   - **Skills extraction** is performed using keyword matching and regular expressions, comparing the content to a pre-defined **skills list**.

2. **Job Description Matching:**
   - **Job descriptions (JDs)** are compared with parsed resumes.
   - The system calculates a **match score** based on the skills found in both the resume and the JD.
   - Key metrics include **skills match**, **missing skills**, and **overall fit**.

3. **SRE-Driven Metrics & Monitoring:**
   - Integrated with **Prometheus** to track essential metrics like **request success rates**, **latency**, and **error rates** for the application.
   - **Histograms** and **counters** capture performance data such as request processing time and HTTP status codes.
   - The **Prometheus metrics endpoint** allows local monitoring of the application's performance.

4. **SLO, SLA, and SLI Integration:**
   - The platform incorporates **Service Level Objectives (SLOs)** for high **availability** and low **latency**.
   - **Service Level Indicators (SLIs)** are used to track performance, and **Service Level Agreements (SLAs)** ensure agreed-upon service levels are met.
   - Examples include: 
     - **99% uptime** (Availability SLO)
     - **95th percentile request latency** should be under 2 seconds.

5. **Autohealing & Chaos Engineering:**
   - **Chaos Engineering** is used to simulate failures and disruptions to test the system's resilience.
   - **Autohealing** mechanisms automatically restart failed services or containers, ensuring **zero downtime** and **high availability**.

## **Architecture:**

- **Frontend**: 
  - A **web-based UI** where users can upload resumes and job descriptions (JDs) to interact with the platform.
  - Results are presented in tables with match scores and missing skills for easy comparison.

- **Backend**:
  - Built with **Flask**, a lightweight Python web framework, which handles resume parsing, skill extraction, and job description comparison.
  - **Prometheus client libraries** are used to expose metrics to Prometheus, allowing local performance monitoring.

- **Chaos & Autohealing**:
  - **Chaos Engineering** tools like **Gremlin** or **Chaos Mesh** are integrated into the local environment to simulate failures and test resilience.
  - **Autohealing** is implemented through **Docker** container orchestration, where containers are restarted automatically if they fail or become unresponsive.

## **SLOs, SLAs, and SLIs:**
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

## **Technologies Used:**

- **Backend**: Python, Flask, Prometheus (for monitoring), Docker
- **Frontend**: HTML, CSS, Jinja templating
- **Resume Parsing**: PDFplumber, python-docx (for parsing PDF and DOCX files)
- **Metrics Monitoring**: Prometheus, Grafana (for local dashboards)
- **Chaos Engineering & Autohealing**: Gremlin, Docker Swarm (for local orchestration)

## **Project Flow:**

### **Job Seeker Workflow:**
1. **Step 1**: Job seekers upload their resumes in **PDF** or **DOCX** format.
2. **Step 2**: The platform extracts the content and compares the skills with the uploaded job description (JD).
3. **Step 3**: A **matching score** is generated, highlighting the skills the job seeker has and those they need to improve.
4. **Step 4**: The results are displayed, showing the matched and missed skills.

### **Hiring Team Workflow:**
1. **Step 1**: Hiring teams upload **job descriptions (JDs)** for available positions.
2. **Step 2**: Job seekers' resumes are uploaded, and the platform compares them against the JDs.
3. **Step 3**: A ranked list of job seekers is generated based on their skill match with the JD.
4. **Step 4**: The hiring team reviews the results and shortlists candidates based on the match scores.

## **Local Deployment:**
This project is designed for **local deployment** and can be run on your local machine or local server. It provides an easy-to-use **web interface** for job seekers and hiring teams to interact with the platform. The application is packaged in **Docker** containers for easy deployment, and **Prometheus** can be used to monitor application performance locally.

### **Steps for Local Deployment:**
1. **Clone the repository**: Clone this repository to your local machine.
2. **Install Docker**: Ensure Docker is installed on your local machine to run the application in containers.
3. **Build the Docker image**: Use `docker build -t sre-app .` to build the image.
4. **Run the container**: Use `docker run -p 8080:8080 sre-app` to start the application.
5. **Access the application**: Open a browser and go to `http://localhost:8080` to start using the platform.
6.Run the command 
```
 docker compose up --build

 This will:

  - Build the Docker image for sre-app (if not already built).
  - Start the sre-app and prometheus services.
  - Expose the application on http://localhost:8080 and Prometheus on http://localhost:9090.
  
```

## **Conclusion:**

This platform is a comprehensive solution for both **job seekers** and **hiring teams**, designed to optimize the resume matching process using modern tools for **monitoring**, **automation**, and **resilience testing**. By integrating **SRE practices**, **chaos engineering**, and **autohealing**, the platform guarantees **high availability**, **low latency**, and **robust performance**, ensuring the recruitment process is efficient and scalable. 

This version of the platform is optimized for **local deployment** and provides a hands-on way to test and monitor the service locally.