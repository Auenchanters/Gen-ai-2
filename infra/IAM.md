# IAM & security model

GridPulse runs on Cloud Run as a dedicated, **least-privilege** service account
(`gridpulse-run@<project>.iam.gserviceaccount.com`) created by
[`infra/deploy.sh`](deploy.sh). No service-account keys are created or stored — Cloud Run
provides credentials via the attached service account (and local dev uses Application
Default Credentials).

## Roles granted to the runtime service account

| Role | Why |
| ---- | --- |
| `roles/bigquery.dataViewer` | read the `gridpulse.forecast` table |
| `roles/bigquery.jobUser` | run the read query |
| `roles/aiplatform.user` | call Gemini on Vertex AI for `/api/ask` |

That is the complete set — no project-wide editor/owner, no write access to BigQuery, no
storage admin. The service only ever *reads* the forecast table and *calls* Gemini.

## Other security posture

- **No secrets in the repo.** Configuration is via environment variables; credentials are
  ambient (service account / ADC). See [`.env.example`](../.env.example).
- **Container runs as a non-root user** (`appuser`) — see the [Dockerfile](../Dockerfile).
- **Input validation** at the API edge via Pydantic bounds (`server/schemas.py`).
- **Security headers + restrictive CORS** on every response (`server/main.py`).
- **Graceful degradation:** with `USE_BIGQUERY=0` / `USE_GEMINI=0` the service runs with no
  cloud access at all (local parquet + rule-based answers), which is also how CI tests it.
