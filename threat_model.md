# STRIDE Threat Model: MWIS Weather Agent

## 1. System Boundaries

### Entry Points
- **Web Interface (ADK Dev UI)**: The user interface where natural language queries are submitted.
- **Agent Server (FastAPI)**: Receives natural language queries, handles routing and invocation of the LLM and function nodes.
- **Database (SQLite)**: Stores cached MWIS forecasts.

### Data Storage Layers
- **Local Filesystem/SQLite**: Caches parsed forecast data to prevent rate-limiting MWIS servers.
- **Logs**: Standard application output logs.

### External Dependencies
- **MWIS Website**: For fetching live forecast HTML pages.
- **Google Gemini API**: For natural language processing and intent extraction.

---

## 2. STRIDE Evaluation

### Spoofing (Caller Identity)
- **Threat**: An attacker could spoof requests to the agent server or spoof the MWIS website to feed malicious HTML into the cache.
- **Mitigation**:
  - The API server expects requests on an internal loopback or behind an authenticated gateway when deployed.
  - MWIS data is fetched over HTTPS to ensure data authenticity.

### Tampering (Data Manipulation)
- **Threat**: An attacker with filesystem access could manipulate `mwis_forecasts.db` to alter returned forecasts.
- **Mitigation**:
  - The SQLite database is stored locally with strict file permissions. The containerized deployment should ensure the filesystem is read-only except for the `cache/` directory.

### Repudiation
- **Threat**: Users making specific requests cannot be audited if logs are insufficient.
- **Mitigation**:
  - Logging captures incoming query requests and their routing traces through the ADK workflow.
  - Adding persistent auth logging in the future (if tied to users) would improve non-repudiation.

### Information Disclosure
- **Threat**: PII leakage or API Key exposure in logs/stack traces.
- **Mitigation**:
  - `GEMINI_API_KEY` is loaded from the environment and is never printed in logs.
  - Application logic suppresses verbose error stack traces from externalizing to the client.

### Denial of Service
- **Threat**: An attacker sends thousands of requests, exhausting API quotas or overwhelming the SQLite cache update mechanism.
- **Mitigation**:
  - The local cache prevents repeated requests to the MWIS website.
  - To prevent Gemini API quota exhaustion, rate limiting should be enforced at the ingress/API gateway layer in production.

### Elevation of Privilege
- **Threat**: An unauthenticated user accesses privileged tool actions or system operations.
- **Mitigation**:
  - The agent only runs safe, isolated python queries against web HTML and local SQLite databases. It cannot execute arbitrary code or shell commands on the host.

---

## 3. Recommendations
1. **Enforce Rate Limiting**: Ensure the production deployment includes an API Gateway with strict rate limits.
2. **Read-Only Filesystem**: Containerize the deployment with a read-only root filesystem, mounting only `/app/cache` as writable.
3. **API Key Rotation**: Periodically rotate the Gemini API key used in production.
