# WorkRelay

**WorkRelay is an agentic operational incident coordination system that uses Gemini 3.5 Flash and Google ADK to select an appropriate incident-response workflow, while keeping operational execution deterministic, controlled, testable, and auditable.**

> **Current deployment:** WorkRelay is deployed privately on Google Cloud Run, using Gemini 3.5 Flash through Google ADK for workflow selection and Firestore for persistent incident state.
>
> **Web console:** WorkRelay also includes a browser-based Operations Console for incident intake, status monitoring, recent-incident review, and detailed lifecycle inspection. The new web UI has been verified locally; the Cloud Run deployment still needs to be rebuilt and redeployed with the UI changes.

## What WorkRelay does

WorkRelay receives an operational incident and coordinates its response through a controlled multi-step workflow.

The system separates **AI decision-making** from **operational execution**:

```text
                    Browser
                       |
                       v
          WorkRelay Operations Console
                       |
                       v
                 FastAPI / CLI
                       |
                       v
              IncidentCoordinator
                       |
                       v
                Decision Provider
                  |             |
                  v             v
            Local Provider   Gemini + ADK
                  |             |
                  +------+------+
                         |
                         v
                  Workflow Registry
                         |
                         v
              Deterministic Workflow
                  |             |
                  v             v
            Investigation   Remediation
                  |             |
                  +------+------+
                         |
                         v
                    Verification
                    |          |
                    v          v
                 RESOLVED   ESCALATED
                         |
                         v
                      Firestore
```

### Key design principle

> **Gemini recommends the workflow; deterministic application logic executes it.**

Gemini does not directly execute arbitrary remediation commands. The application validates the selected workflow against the registered workflow definitions and then executes controlled workflow steps.

This separation makes WorkRelay easier to test, reason about, secure, and extend.

---

## Web Operations Console

WorkRelay now includes a browser-based **Operations Console** built on top of the existing FastAPI application.

The console provides an operator-friendly interface for interacting with the incident coordination system without requiring direct API or CLI commands.

### Current UI capabilities

- System health indicator
- Browser-based incident intake
- Incident title, service, severity, and description fields
- Incident creation and coordination
- Dashboard summary statistics:
  - Total incidents
  - Active incidents
  - Resolved incidents
  - Escalated incidents
- Five most recent incidents on the main dashboard
- Incident status, severity, workflow, provider, and retry information
- Incident detail view
- Gemini coordination reasoning
- Full incident lifecycle timeline
- Resolution information
- Responsive layout for smaller screens

### UI architecture

```text
Browser
   |
   v
GET /
   |
   v
WorkRelay Operations Console
   |
   +----------------------+
   |                      |
   v                      v
GET /health          POST /incidents
   |                      |
   |                      v
   |               IncidentCoordinator
   |                      |
   |                      v
   |               Gemini / Local Provider
   |                      |
   |                      v
   |               Workflow Execution
   |                      |
   |                      v
   +----------------> Firestore
```

### Run the web console locally

After installing dependencies:

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

The console uses the same backend as the API and CLI, so incidents created from the browser follow the same coordination and workflow logic.

### Example browser execution

A real local browser submission was completed with:

```text
Incident ID : INC-513D1311
Severity    : HIGH
Workflow    : high_severity_incident
Status      : RESOLVED
Provider    : GeminiDecisionProvider
Retries     : 0
```

The incident also displayed Gemini coordination reasoning and the complete lifecycle:

```text
WORKFLOW_SELECTED
INCIDENT_CLASSIFIED
INVESTIGATION_STARTED
REMEDIATION_STARTED
VERIFICATION_STARTED
INCIDENT_RESOLVED
```

This demonstrates that the web console is connected to the real WorkRelay coordination path rather than being a static mockup.

---

## What has been demonstrated

- Gemini 3.5 Flash makes the incident workflow coordination decision.
- Google ADK provides the agent integration.
- Deterministic workflow execution handles investigation, remediation, and verification.
- Retry and recovery behavior is implemented and tested.
- Failed recovery triggers escalation.
- Incident lifecycle history is recorded.
- Local JSON-backed state is supported.
- Firestore persistence is implemented and verified.
- The browser-based Operations Console is implemented.
- Browser incident creation and coordination have been verified locally.
- The UI displays Gemini decision-provider information and coordination reasoning.
- The UI displays incident lifecycle history and resolution details.
- The application is deployed to Google Cloud Run.
- Cloud Run uses a dedicated runtime service account.
- The Cloud Run service is private.
- Cloud Run is configured to scale to zero with a maximum of one instance.
- The container is stored in Google Artifact Registry.
- The deployed container is referenced by an immutable image digest.
- The deployed Gemini workflow has been tested end-to-end.
- The resulting incident has been independently verified in Firestore.
- Automated test suite: **32 passed** before the web-console changes; the final UI-inclusive suite must be rerun before the next release commit.

---

## Current status

| Component | Status |
|---|---|
| FastAPI incident API | ✅ Implemented and tested |
| CLI incident runner | ✅ Implemented and tested |
| Local decision provider | ✅ Implemented |
| Gemini + Google ADK provider | ✅ Implemented |
| Gemini model | ✅ `gemini-3.5-flash` |
| Gemini access | ✅ Google Cloud / Vertex AI |
| Decision provider selection | ✅ `local` / `gemini` |
| State store selection | ✅ `local` / `firestore` |
| Deterministic workflow engine | ✅ Implemented |
| Retry and recovery | ✅ Implemented and tested |
| Escalation | ✅ Implemented and tested |
| Incident lifecycle history | ✅ Implemented |
| Firestore state store | ✅ Implemented and verified |
| Operations Console | ✅ Implemented and locally verified |
| Browser incident intake | ✅ Verified |
| Dashboard statistics | ✅ Implemented |
| Incident detail/timeline | ✅ Implemented |
| Automated tests | ⚠️ 32 passed before latest UI changes; final suite pending |
| Artifact Registry | ✅ Image previously built and pushed |
| Cloud Run backend | ✅ Deployed and verified |
| Cloud Run UI deployment | ⏳ New UI image still needs deployment |
| Cloud Run access | 🔒 Private |
| Cloud Run scaling | ✅ Scale-to-zero, max 1 instance |
| Pub/Sub | ⏳ Not yet provisioned |
| Production observability | ⏳ Future work |
| Public endpoint | ❌ Intentionally not enabled |
| Production authentication/authorization | ⏳ Future work |

---

## Agentic workflow

For an incoming incident, WorkRelay:

1. Creates the incident.
2. Sends the incident context to the configured decision provider.
3. Selects an approved workflow.
4. Persists the selected workflow and coordination reasoning.
5. Classifies the incident.
6. Investigates the incident.
7. Performs remediation.
8. Verifies recovery.
9. Retries when the selected workflow allows retries.
10. Escalates when recovery cannot be completed.
11. Records lifecycle events and final state.
12. Persists the final incident state.

A successful Gemini-powered execution produces a result similar to:

```text
Provider      : GeminiDecisionProvider
Workflow      : high_severity_incident
Status        : RESOLVED
Current Step  : incident_resolved
Retries       : 0
```

---

## Reliability model

WorkRelay treats incident handling as a stateful workflow rather than a single AI response.

```text
OPEN
 |
 v
CLASSIFYING
 |
 v
INVESTIGATING
 |
 v
REMEDIATING
 |
 v
VERIFYING
 |
 +----------------------+
 |                      |
 v                      v
RESOLVED             FAILURE
                        |
                        v
                     RETRY?
                    /      \
                  YES       NO
                   |         |
                   v         v
                 RETRY    ESCALATED
                   |
                   v
              VERIFICATION
                   |
             +-----+-----+
             |           |
             v           v
          RESOLVED    ESCALATED
```

The workflow engine owns state transitions and recovery behavior.

The AI decision layer does not bypass those controls.

---

## Decision providers

### Local provider

The local provider is deterministic and requires no Google Cloud credentials.

It is useful for:

- local development
- automated testing
- offline demonstrations
- deterministic workflow testing
- avoiding unnecessary Gemini usage

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

For local development, authenticate using Application Default Credentials:

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/cloud-platform
```

Do not commit credentials, access tokens, API secrets, or service-account private keys to the repository.

---

## State stores

### Local state store

The local state store provides JSON-backed persistence for development and testing.

```bash
export WORKRELAY_STATE_STORE=local
```

### Firestore state store

The production deployment uses Google Cloud Firestore.

```bash
export WORKRELAY_STATE_STORE=firestore
```

The deployed WorkRelay runtime uses the dedicated service account:

```text
workrelay-runtime@workrelay.iam.gserviceaccount.com
```

The runtime service account has the required permissions for:

```text
roles/aiplatform.user
roles/datastore.user
```

No project-level Editor or Owner role is assigned to the WorkRelay runtime service account.

---

## Google Cloud deployment

WorkRelay is currently deployed as a private Cloud Run service.

### Deployed components

- Google Cloud project: `workrelay`
- Cloud Run service: `workrelay`
- Firestore Native database
- Artifact Registry repository
- WorkRelay container image
- Gemini 3.5 Flash through Google ADK
- Dedicated WorkRelay runtime service account

### Cloud Run configuration

The current backend deployment uses:

```text
CPU              : 1
Memory           : 512 MiB
Minimum instances: 0
Maximum instances: 1
Access           : Private
Region           : europe-west1
Gemini endpoint  : global
```

The service is intentionally **not public**.

This protects the current development deployment from unauthenticated external requests and unnecessary usage.

### Deployment verification

The previously verified backend revision was:

```text
workrelay-00001-4xg
```

The revision used the Artifact Registry image by immutable digest:

```text
sha256:bb2f302543c528f573edbc16ea4ae9aef2bb430bf5d81a9d2b2be3ef6e73404b
```

The **web-console changes are not yet represented by this deployed image**. A new container build and Cloud Run revision are required before claiming the browser UI is deployed to Cloud Run.

---

## End-to-end cloud verification

A real incident was previously submitted through the deployed Cloud Run service using Gemini.

Example result:

```text
Incident ID : INC-AB0E4A95
Title       : Cloud Run Gemini test
Service     : payment-api
Severity    : HIGH
Workflow    : high_severity_incident
Status      : RESOLVED
Current Step: incident_resolved
Retries     : 0
```

Gemini coordination:

```text
Provider : GeminiDecisionProvider

Reason:
The incident severity is HIGH, which requires the
high_severity_incident workflow for cautious coordination
and verification.
```

The incident lifecycle included:

```text
WORKFLOW_SELECTED
INCIDENT_CLASSIFIED
INVESTIGATION_STARTED
REMEDIATION_STARTED
VERIFICATION_STARTED
INCIDENT_RESOLVED
```

The resulting incident was independently verified in Firestore after the Cloud Run execution.

This demonstrates the previously verified cloud backend path:

```text
Client
  |
  v
Cloud Run
  |
  v
FastAPI
  |
  v
Gemini + ADK
  |
  v
Workflow selection
  |
  v
Deterministic execution
  |
  v
Firestore persistence
```

The next deployment verification will extend this path to include the browser Operations Console.

---

## Local setup

### Requirements

- Python 3.11+
- Git
- Google Cloud CLI (`gcloud`) for Gemini/Firestore development
- Google Cloud project access when using Gemini or Firestore

### Clone the repository

```bash
git clone https://github.com/Yemmmyc/workrelay.git
cd workrelay
```

### Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the test suite

Run:

```bash
pytest -q
```

The previously completed suite produced:

```text
32 passed
```

The suite covers:

- workflow selection
- state-store behavior
- incident lifecycle
- workflow resolution
- retry and recovery
- escalation
- persistence
- API behavior
- state-store factory behavior
- Firestore state-store behavior
- Gemini decision validation

The test run also produces a small number of dependency deprecation warnings. These originate from dependencies such as Starlette, OpenTelemetry, and Google ADK and do not represent failing WorkRelay tests.

**Before the next release commit, rerun the full suite after the web-console changes and update the documented count if the test total changes.**

---

## Run the web application locally

The browser Operations Console is served by FastAPI.

Start the application:

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

The UI is backed by the same incident API and coordination engine used by the CLI.

### Recommended Gemini + Firestore configuration

```bash
export WORKRELAY_DECISION_PROVIDER=gemini
export WORKRELAY_STATE_STORE=firestore
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=workrelay
export GOOGLE_CLOUD_LOCATION=global
```

Then start:

```bash
uvicorn app.main:app --reload --port 8000
```

### Browser workflow

1. Open the Operations Console.
2. Confirm `SYSTEM HEALTHY`.
3. Enter an incident title.
4. Enter the affected service.
5. Select a severity.
6. Describe the incident.
7. Click **Create & Coordinate Incident**.
8. Review the resulting incident.
9. Select **View Details** to inspect Gemini reasoning and lifecycle events.

---

## Run the API locally

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "workrelay"
}
```

### Create an incident

```bash
curl -X POST http://127.0.0.1:8000/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Payment API failure",
    "description": "Payment requests are failing.",
    "service": "payment-api",
    "severity": "HIGH"
  }'
```

### List incidents

```bash
curl http://127.0.0.1:8000/incidents
```

### Retrieve an incident

```bash
curl http://127.0.0.1:8000/incidents/INC-XXXXXXXX
```

---

## Run an incident from the CLI

For local deterministic execution:

```bash
WORKRELAY_DECISION_PROVIDER=local \
WORKRELAY_STATE_STORE=local \
python run.py \
  --title "Payment API failure" \
  --description "Payment requests are failing." \
  --service payment-api \
  --severity high
```

For Gemini-powered execution:

```bash
WORKRELAY_DECISION_PROVIDER=gemini \
WORKRELAY_STATE_STORE=local \
GOOGLE_GENAI_USE_ENTERPRISE=TRUE \
GOOGLE_CLOUD_PROJECT=workrelay \
GOOGLE_CLOUD_LOCATION=global \
python run.py \
  --title "Payment API failure" \
  --description "Payment requests are failing." \
  --service payment-api \
  --severity high
```

The CLI reports:

- incident ID
- severity
- selected workflow
- status
- current step
- retry count
- resolution
- coordination provider
- Gemini reasoning
- workflow metadata

---

## Failure simulation

WorkRelay supports deterministic failure simulation for demonstrating reliability behavior.

View available CLI options:

```bash
python run.py --help
```

Failure scenarios can demonstrate:

```text
Action failure
      |
      v
Retry scheduled
      |
      v
Recovery
      |
      v
RESOLVED
```

or:

```text
Action failure
      |
      v
Retry limit reached
      |
      v
Escalation
      |
      v
ESCALATED
```

This is an important part of the project because WorkRelay is designed to demonstrate **multi-step autonomous coordination and failure handling**, rather than simply returning a chatbot response.

---

## Operational action model

The current action implementations are deliberately deterministic.

The action layer currently provides:

- investigation simulation
- remediation simulation
- verification simulation
- controlled failure injection for testing

The deployed application therefore demonstrates the **coordination architecture and reliability workflow**, while avoiding uncontrolled changes to real infrastructure.

The action boundaries are designed to be replaced or augmented later with real operational adapters such as:

- service health checks
- logs
- metrics
- traces
- incident-management systems
- deployment systems
- Kubernetes operations
- infrastructure automation

This separation allows real operational integrations to be introduced without giving the language model unrestricted execution authority.

---

## Security

Current security controls include:

- Application Default Credentials for local Google Cloud authentication.
- No service-account private keys stored in the repository.
- No API keys committed to Git.
- `.env` files excluded through `.gitignore`.
- Dedicated WorkRelay runtime service account.
- Least-privilege runtime permissions.
- Private Cloud Run service.
- No `allUsers` Cloud Run IAM binding.
- Cloud Run resource limits.
- Local deterministic provider for development without external AI calls.

The repository was checked for common credential patterns, including API keys, tokens, passwords, private-key blocks, and service-account credential files. No committed credentials were found.

### Before public production exposure

The application should gain:

- authentication and authorization
- structured logging
- monitoring and alerting
- stronger request controls
- production secret-management mechanisms
- additional endpoint protection

Secret management should continue to use Google Cloud identity and managed secret mechanisms rather than repository-stored credentials.

---

## Cost control

WorkRelay is being developed with cost awareness.

Current controls include:

- Gemini Flash is used for the decision layer.
- Local mode avoids Gemini calls during normal development and testing.
- Cloud Run is configured with scale-to-zero.
- Cloud Run maximum instances are currently limited to one.
- Firestore is used for persistent state without unnecessary duplicate storage.
- Billing budget alerts are configured on the billing account.
- Unnecessary repeated Gemini calls are avoided during development.

The current deployment is intentionally small and private.

---

## Project structure

```text
workrelay/
├── app/
│   ├── agent/
│   │   ├── coordinator.py
│   │   ├── decision.py
│   │   ├── prompts.py
│   │   └── provider_factory.py
│   │
│   ├── actions/
│   │   ├── incident_actions.py
│   │   └── notification_actions.py
│   │
│   ├── services/
│   │   ├── state_store.py
│   │   ├── state_store_interface.py
│   │   ├── state_store_factory.py
│   │   └── firestore_state_store.py
│   │
│   ├── workflows/
│   │   ├── registry.py
│   │   └── incident_workflow.py
│   │
│   ├── models/
│   │   └── incident.py
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   ├── static/
│   │   └── style.css
│   │
│   ├── api.py
│   └── main.py
│
├── tests/
│   ├── test_actions.py
│   ├── test_api.py
│   ├── test_firestore_state_store.py
│   ├── test_state_store_factory.py
│   └── test_workflow.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEMO.md
│   ├── DEVELOPMENT.md
│   └── HACKATHON.md
│
├── data/
│   └── .gitkeep
│
├── run.py
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Architecture and documentation

Additional documentation is available in the repository:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system architecture, components, data flow, UI integration, and design decisions
- [`docs/DEMO.md`](docs/DEMO.md) — demonstration flow, browser workflow, and evidence
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — development, testing, local UI setup, and troubleshooting
- [`docs/HACKATHON.md`](docs/HACKATHON.md) — original hackathon context and requirements

These documents should be kept synchronized with the deployed application as the project evolves.

---

## Current Google Cloud state

### Deployed and verified

- Google Cloud project
- Cloud Run service
- Artifact Registry repository and WorkRelay image
- Gemini 3.5 Flash through Google ADK
- Firestore Native database
- Dedicated WorkRelay runtime service account
- Private Cloud Run access
- Scale-to-zero configuration
- End-to-end Cloud Run → Gemini → workflow → Firestore execution

### Implemented locally but awaiting new cloud deployment

- Browser Operations Console
- Browser incident intake
- Dashboard statistics
- Incident detail/timeline interface
- UI styling and static assets

### Configured but not yet deployed/provisioned

- Pub/Sub event-driven incident intake
- Production observability and alerting
- Public production endpoint
- Production authentication and authorization

The repository intentionally distinguishes **deployed infrastructure** from **implemented-but-not-yet-deployed features** and planned future infrastructure.

---

## Roadmap

1. Rebuild the container with the Operations Console included.
2. Deploy the updated image to Cloud Run.
3. Verify the browser UI through the deployed Cloud Run service.
4. Add automated tests for important UI-serving and integration behavior where appropriate.
5. Add Pub/Sub for event-driven incident intake.
6. Add production-grade observability and structured logs.
7. Add API authentication and authorization.
8. Validate retry and escalation behavior in the deployed environment.
9. Replace deterministic operational actions with real operational adapters.
10. Add stronger idempotency and duplicate-incident protection.
11. Expand operational integrations while maintaining controlled execution boundaries.

---

## Design philosophy

WorkRelay is intentionally designed around separation of concerns:

| Layer | Responsibility |
|---|---|
| Browser Operations Console | Human-friendly incident intake and operational visibility |
| Gemini / Google ADK | Intelligent workflow selection |
| Decision Provider | Provides an approved coordination decision |
| Coordinator | Connects decision-making to workflow execution |
| Workflow Registry | Defines approved workflows |
| Deterministic Workflow Engine | Executes state transitions and recovery |
| Action Layer | Performs controlled operational actions |
| State Store | Persists incident state |
| FastAPI | HTTP interface |
| CLI | Local/operator interface |
| Firestore | Cloud persistence |
| Cloud Run | Managed application runtime |

The goal is to build an agentic system that can make useful operational decisions while keeping execution **controlled, testable, auditable, and extensible**.

---

## Portfolio summary

**WorkRelay demonstrates an agentic incident-response architecture using Gemini 3.5 Flash, Google ADK, FastAPI, Firestore, Artifact Registry, and Cloud Run. Gemini selects an approved response workflow, while deterministic application logic controls investigation, remediation, verification, retry, escalation, and lifecycle persistence. A browser-based Operations Console provides incident intake, operational visibility, Gemini reasoning, and lifecycle inspection over the same backend.**

The project has been tested locally and deployed to Google Cloud with a private Cloud Run service and dedicated least-privilege runtime identity. The next release step is to deploy the new web console alongside the existing cloud backend.

---

## License

This project is currently maintained as a personal portfolio and demonstration project.
