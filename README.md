# WorkRelay

WorkRelay is an automated operational incident coordination system for the Google All Things Agentic Hackathon — The Taskmaster track.

It receives incidents, selects an appropriate response workflow, executes deterministic remediation and verification steps, and records the resulting state.

## Current status

- FastAPI incident API: implemented and tested
- Deterministic local decision provider: implemented
- Gemini + Google ADK decision provider: implemented
- Gemini model: `gemini-3.5-flash`
- Configurable `local` / `gemini` provider factory: implemented
- Deterministic workflow engine: implemented
- Retry and escalation paths: implemented
- Local JSON-backed state: implemented
- Application factory: implemented
- Automated tests: **25 passing**
- Google Cloud deployment: intentionally pending hackathon credits

## Architecture

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

The key design principle is:

> Gemini recommends the workflow; deterministic application logic executes it.

## Local setup

```bash
cd ~/projects/workrelay
source .venv/bin/activate
pytest -q
```

Expected current result:

```text
25 passed
```

## Run the API

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
    "description": "Payment requests are returning HTTP 500 errors.",
    "service": "payment-api",
    "severity": "HIGH"
  }'
```

## Decision providers

Local mode is the default and requires no credentials:

```bash
WORKRELAY_DECISION_PROVIDER=local
```

Gemini mode:

```bash
WORKRELAY_DECISION_PROVIDER=gemini
```

Gemini is isolated behind the decision-provider interface. Its response is validated against the registered workflows before execution.

## Project structure

```text
workrelay/
├── app/
│   ├── actions/
│   ├── agent/
│   │   ├── coordinator.py
│   │   ├── decision.py
│   │   ├── prompts.py
│   │   └── provider_factory.py
│   ├── models/
│   ├── services/
│   ├── workflows/
│   ├── api.py
│   └── main.py
├── tests/
├── data/
├── docs/
├── .env.example
├── requirements.txt
└── run.py
```

## Cloud status

Cloud deployment is deliberately deferred until the hackathon Google Cloud credits are available.

The intended next cloud components are Cloud Run, Firestore and Pub/Sub. They should not be represented as deployed until they have actually been configured and tested.

See:

- [Architecture](docs/ARCHITECTURE.md)
- [Demo](docs/DEMO.md)
- [Hackathon](docs/HACKATHON.md)
- [Development](docs/DEVELOPMENT.md)
