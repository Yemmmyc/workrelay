# WorkRelay

WorkRelay is an automated operational incident coordination system built around an agentic workflow: it receives an incident, uses Gemini to select an appropriate response workflow, executes deterministic remediation and verification steps, records lifecycle state, and resolves or escalates the incident.

## Current status

- FastAPI incident API: implemented and tested
- CLI incident runner: implemented and tested
- Deterministic local decision provider: implemented
- Gemini + Google ADK decision provider: implemented
- Gemini model: `gemini-3.5-flash`
- Gemini access: Google Cloud / Vertex AI using the global endpoint
- Configurable decision provider: `local` / `gemini`
- Configurable state store: `local` / `firestore`
- Deterministic workflow engine: implemented
- Retry and escalation paths: implemented
- Incident lifecycle history: implemented
- Local JSON-backed state store: implemented
- Firestore state store: implemented
- Application factory: implemented
- Google Cloud project and required APIs: configured
- Dedicated WorkRelay runtime service account: configured
- Automated tests: **32 passed**
- Real end-to-end Gemini test: **successful**
- Cloud Run deployment: **not yet deployed**
- Pub/Sub: **not yet provisioned**

## What WorkRelay does

WorkRelay separates **AI decision-making** from **operational execution**.

```text
Incident
   |
   v
FastAPI / CLI
   |
   v
IncidentCoordinator
   |
   v
Decision Provider
   |----------------------|
   |                      |
   v                      v
Local Provider       Gemini + ADK
   |                      |
   +----------+-----------+
              |
              v
      Workflow Registry
              |
              v
    Deterministic Workflow
              |
       +------+------+
       |             |
       v             v
  Remediation    Verification
       |             |
       +------+------+
              |
              v
       Resolved / Escalated
```

### Key design principle

> **Gemini recommends the workflow; deterministic application logic executes it.**

Gemini does not directly perform arbitrary remediation. The application validates the selected workflow and then runs predefined workflow steps. This makes the system easier to test, reason about, and extend safely.

## Agentic workflow

For an incoming incident, WorkRelay:

1. Creates and persists the incident.
2. Sends incident context to the configured decision provider.
3. Selects one registered workflow.
4. Executes the workflow's investigation/remediation steps.
5. Verifies the result.
6. Retries where configured.
7. Escalates when recovery cannot be completed.
8. Records lifecycle history and final state.

Example successful Gemini run:

```text
Provider : GeminiDecisionProvider
Workflow : high_severity_incident
Status   : RESOLVED
Current Step: incident_resolved
```

## Decision providers

### Local provider

The local provider is deterministic and requires no Google Cloud credentials.

```bash
export WORKRELAY_DECISION_PROVIDER=local
```

### Gemini provider

The Gemini provider uses Google ADK and Gemini 3.5 Flash through Google Cloud.

```bash
export WORKRELAY_DECISION_PROVIDER=gemini
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=workrelay
export GOOGLE_CLOUD_LOCATION=global
```

For local development, authenticate with Application Default Credentials:

```bash
gcloud auth application-default login   --scopes=https://www.googleapis.com/auth/cloud-platform
```

Do not commit credentials, access tokens, or service-account private keys to the repository.

## State stores

### Local

```bash
export WORKRELAY_STATE_STORE=local
```

The local store is useful for development and testing.

### Firestore

```bash
export WORKRELAY_STATE_STORE=firestore
```

The Firestore database is configured in the Google Cloud `workrelay` project.

The application uses the dedicated runtime service account:

```text
workrelay-runtime@workrelay.iam.gserviceaccount.com
```

with the required roles for Vertex AI access and Firestore data access.

## Local setup

Requirements:

- Python 3.11+
- Google Cloud CLI (`gcloud`) for Gemini/Firestore development
- Google Cloud project access when using Gemini or Firestore

```bash
cd ~/projects/workrelay
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the test suite:

```bash
pytest -q
```

Expected result:

```text
32 passed
```

## Run the API

Start FastAPI with:

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Create an incident:

```bash
curl -X POST http://127.0.0.1:8000/incidents   -H "Content-Type: application/json"   -d '{
    "title": "Payment API failure",
    "description": "Payment requests are failing.",
    "service": "payment-api",
    "severity": "high"
  }'
```

List incidents:

```bash
curl http://127.0.0.1:8000/incidents
```

## Run an incident from the CLI

Example:

```bash
WORKRELAY_DECISION_PROVIDER=gemini GOOGLE_GENAI_USE_ENTERPRISE=TRUE GOOGLE_CLOUD_PROJECT=workrelay GOOGLE_CLOUD_LOCATION=global python run.py   --title "Payment API failure"   --description "Payment requests are failing."   --service payment-api   --severity high
```

The CLI prints the incident ID, selected workflow, status, retries, resolution, and Gemini coordination reasoning.

## Simulating failures

The local workflow supports failure simulation for testing retry and escalation behavior.

Use the CLI help to see the available options:

```bash
python run.py --help
```

These scenarios are useful for demonstrating that WorkRelay does more than produce a chatbot response: it executes a multi-step workflow and handles failure paths.

## Google Cloud status

The Google Cloud project is configured for WorkRelay.

Configured components include:

- Cloud Run API
- Firestore API
- Vertex AI API
- Pub/Sub API
- Artifact Registry API
- Cloud Build API
- Firestore Native database
- Dedicated WorkRelay runtime service account

### Not yet deployed

The following are intentionally not described as deployed:

- Cloud Run service
- Pub/Sub topics/subscriptions
- Production observability
- Public production endpoint

This README reflects the actual current state rather than treating planned architecture as deployed infrastructure.

## Security

Current development approach:

- Use Application Default Credentials locally.
- Do not store service-account private keys in the repository.
- Use a dedicated WorkRelay runtime service account for Google Cloud workloads.
- Grant only the roles required by the application.
- Keep `.env` files and secrets out of Git.
- Do not expose credentials in screenshots, logs, or demo recordings.

Before production deployment, add authentication/authorization, secret management, structured logging, monitoring, and additional endpoint protection.

## Cost control

WorkRelay is being developed with cost awareness.

- Gemini Flash is used for the decision layer.
- Local mode is available for tests and development that do not require Gemini.
- Cloud Run should be configured to scale to zero where appropriate.
- Firestore usage should remain within the available development/free usage where possible.
- Billing budget alerts are configured on the project billing account.
- Avoid unnecessary repeated Gemini calls during development.

## Project structure

```text
workrelay/
├── app/
│   ├── agent/
│   │   ├── coordinator.py
│   │   ├── decision.py
│   │   ├── prompts.py
│   │   └── provider_factory.py
│   ├── services/
│   │   ├── state_store.py
│   │   ├── state_store_interface.py
│   │   ├── state_store_factory.py
│   │   └── firestore_state_store.py
│   ├── workflows/
│   │   ├── registry.py
│   │   └── incident_workflow.py
│   ├── models/
│   │   └── incident.py
│   ├── api.py
│   └── main.py
├── tests/
├── docs/
├── run.py
├── requirements.txt
├── .env.example
└── README.md
```

## Roadmap

1. Deploy the application to Cloud Run.
2. Validate Firestore persistence from the deployed service.
3. Add Pub/Sub for event-driven incident intake.
4. Add production-grade observability and structured logs.
5. Add API authentication and authorization.
6. Validate retry/escalation behavior in the deployed environment.
7. Capture deployment and end-to-end evidence for portfolio/demo use.

## Design philosophy

WorkRelay is intentionally designed around a clear separation of concerns:

- **Gemini / ADK** — intelligent workflow selection
- **Coordinator** — orchestration
- **Workflow registry** — approved workflow definitions
- **Deterministic workflow engine** — execution and recovery
- **State store** — persistence
- **FastAPI / CLI** — interfaces

The goal is an agentic system that can make a useful decision while keeping operational execution controlled, testable, and observable.

## Documentation

- `docs/ARCHITECTURE.md` — system architecture and design decisions
- `docs/DEMO.md` — demonstration flow and evidence
- `docs/DEVELOPMENT.md` — local development and testing
- `docs/HACKATHON.md` — original hackathon context and requirements
