# WorkRelay Demo Guide

## Purpose

This guide provides a repeatable demonstration of WorkRelay's agentic incident-coordination workflow.

The demo focuses on the core behavior that is currently implemented and tested:

```text
Incident
   |
   v
Gemini 3.5 Flash + Google ADK
   |
   v
Workflow selection
   |
   v
Deterministic workflow execution
   |
   v
Remediation
   |
   v
Verification
   |
   v
RESOLVED / RETRY / ESCALATED
```

The important point is that WorkRelay is not demonstrated as a chatbot. Gemini makes the workflow-selection decision, while the application controls and executes the registered operational workflow.

---

## 1. Demo prerequisites

From WSL Ubuntu:

```bash
cd ~/projects/workrelay
source .venv/bin/activate
```

Verify the environment:

```bash
python --version
gcloud --version
```

The local project uses Python 3.11+.

For Gemini demonstrations, Google Application Default Credentials must be available.

Check:

```bash
gcloud auth application-default print-access-token
```

If authentication has not been configured:

```bash
gcloud auth application-default login   --scopes=https://www.googleapis.com/auth/cloud-platform
```

---

## 2. Run the test suite first

Before a demonstration, verify the application:

```bash
pytest -q
```

The current test suite should report:

```text
34 passed
```

There may be dependency deprecation warnings. These do not indicate failed WorkRelay tests.

---

## 3. Demonstrate the local deterministic mode

Local mode is useful for a fast demonstration without making Gemini API calls.

Set:

```bash
export WORKRELAY_DECISION_PROVIDER=local
export WORKRELAY_STATE_STORE=local
```

Run:

```bash
python run.py   --title "Payment API failure"   --description "Payment requests are failing."   --service payment-api   --severity high
```

The result should show:

- incident ID
- incident title
- service
- severity
- selected workflow
- final status
- current workflow step
- retries
- resolution
- coordination information

This mode is deterministic and suitable for repeatable local tests.

---

## 4. Demonstrate the real Gemini workflow

This is the most important current WorkRelay demonstration.

Set the Gemini configuration:

```bash
export WORKRELAY_DECISION_PROVIDER=gemini
export WORKRELAY_STATE_STORE=local
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=workrelay
export GOOGLE_CLOUD_LOCATION=global
```

Then run:

```bash
python run.py   --title "Payment API failure"   --description "Payment requests are failing."   --service payment-api   --severity high
```

The current successful end-to-end demonstration produced:

```text
WORKRELAY INCIDENT RESULT

Incident ID : INC-B3CD3B74
Title       : Payment API failure
Service     : payment-api
Severity    : HIGH
Workflow    : high_severity_incident
Status      : RESOLVED
Current Step: incident_resolved
Retries     : 0
Resolution  : Verification completed for payment-api.
```

The coordination section showed:

```text
Provider : GeminiDecisionProvider
```

and Gemini explained that the HIGH severity incident should use the `high_severity_incident` workflow.

The metadata also showed investigation and verification results.

This proves the current local implementation can perform the complete path:

```text
Gemini decision
      ↓
approved workflow
      ↓
investigation
      ↓
remediation
      ↓
verification
      ↓
resolved incident
```

---

## 5. Demonstrate the Operations Console

The WorkRelay Operations Console provides a browser-based interface for incident intake and operational visibility.

Start the local application:

```bash
export WORKRELAY_DECISION_PROVIDER=local
export WORKRELAY_STATE_STORE=local

uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

The console provides:

- incident creation
- total, active, resolved and escalated incident counts
- recent incident visibility
- severity and status indicators
- selected workflow
- decision-provider information
- retry count
- current workflow step
- coordination reasoning when the Gemini provider is used
- detailed incident lifecycle history

### Real Gemini browser demonstration

For a real Gemini + Firestore browser demonstration, configure:

```bash
export WORKRELAY_DECISION_PROVIDER=gemini
export WORKRELAY_STATE_STORE=firestore
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=workrelay
export GOOGLE_CLOUD_LOCATION=global
```

Start the application:

```bash
uvicorn app.main:app --reload --port 8000
```

Create an incident from the Operations Console. A successful local browser demonstration produced:

```text
Incident ID : INC-513D1311
Status      : RESOLVED
Workflow    : high_severity_incident
Provider    : GeminiDecisionProvider
```

The incident completed:

```text
WORKFLOW_SELECTED
INCIDENT_CLASSIFIED
INVESTIGATION_STARTED
REMEDIATION_STARTED
VERIFICATION_STARTED
INCIDENT_RESOLVED
```

The browser console uses the same FastAPI backend and coordination path as the CLI and API demonstrations. It does not make workflow decisions independently.

---

## 6. What to explain during the Gemini demo

A good spoken explanation is:

> "WorkRelay receives an operational incident and passes the incident context to Gemini through Google ADK. Gemini selects one of the workflows that WorkRelay has registered. The model does not generate arbitrary remediation commands. The coordinator validates the selected workflow and deterministic application logic executes the approved steps. The system then verifies recovery and either resolves, retries, or escalates the incident."

This highlights the controlled-autonomy design.

---

## 6. Demonstrate the FastAPI API

Start the API:

```bash
uvicorn app.main:app --reload
```

In another WSL terminal:

```bash
cd ~/projects/workrelay
source .venv/bin/activate
```

Check health:

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

Retrieve a specific incident:

```bash
curl http://127.0.0.1:8000/incidents/<INCIDENT_ID>
```

Replace `<INCIDENT_ID>` with the ID returned when the incident is created.

---

## 7. Demonstrate failure handling

WorkRelay includes failure simulation specifically so retry and escalation behavior can be demonstrated safely.

First inspect the available options:

```bash
python run.py --help
```

Use the supported failure-simulation flags to demonstrate scenarios such as:

```text
Normal execution
      |
      +----> RESOLVED

Temporary remediation failure
      |
      +----> RETRY
                 |
                 +----> recovery
                         |
                         +----> RESOLVED

Persistent failure
      |
      +----> retries exhausted
                 |
                 +----> ESCALATED
```

This is an important part of the demo because operational automation must account for failure rather than assuming every action succeeds.

Do not simulate failures against a real production service. Use WorkRelay's built-in simulation behavior.

---

## 8. Demonstrate lifecycle history

WorkRelay records lifecycle changes as part of incident state.

During a demo, explain that the incident is not just a final JSON response. The application maintains state as the workflow progresses.

Conceptually:

```text
CREATED
   |
   v
WORKFLOW_SELECTED
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
   v
RESOLVED
```

Failure paths can include retrying and escalation states.

This provides a basis for operational auditing and future observability.

---

## 9. Demonstrate Firestore mode

Firestore is implemented as an alternative state store.

Before using it, ensure Google Cloud authentication and the WorkRelay Firestore database are available.

Set:

```bash
export WORKRELAY_STATE_STORE=firestore
```

Keep the decision provider local if you only want to test Firestore persistence:

```bash
export WORKRELAY_DECISION_PROVIDER=local
```

Then run an incident:

```bash
python run.py   --title "Firestore persistence test"   --description "Testing persistent incident state."   --service demo-service   --severity medium
```

The application will use the Firestore state-store implementation instead of the local JSON-backed store.

For a Gemini + Firestore demonstration:

```bash
export WORKRELAY_DECISION_PROVIDER=gemini
export WORKRELAY_STATE_STORE=firestore
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=workrelay
export GOOGLE_CLOUD_LOCATION=global
```

Then run the same CLI command.

Use this mode only when the Google Cloud environment is intentionally being exercised, because Gemini and cloud persistence can incur usage.

---

## 10. Recommended portfolio demo sequence

A concise 3–5 minute demonstration can follow this sequence.

### Part 1 — Introduce the problem

Explain:

> "WorkRelay is an automated incident-coordination system. Instead of only telling an operator what to do, it selects a workflow, executes controlled steps, verifies recovery, and handles failure."

### Part 2 — Show the Operations Console

Open the browser-based Operations Console and create a high-severity incident. Highlight the incident card, status, selected workflow, provider, and lifecycle details.

### Part 3 — Show the architecture

Open:

```text
docs/ARCHITECTURE.md
```

Briefly show:

```text
FastAPI / CLI
      ↓
Coordinator
      ↓
Gemini + ADK
      ↓
Workflow Registry
      ↓
Deterministic Execution
      ↓
Verification
      ↓
State Store
```

### Part 4 — Show the real Gemini run

Run the Gemini CLI command.

Highlight:

```text
Provider : GeminiDecisionProvider
Workflow : high_severity_incident
Status   : RESOLVED
```

### Part 5 — Show failure handling

Run one of the built-in failure simulations and explain the retry/escalation path.

### Part 6 — Show the API

Open the health endpoint and create/list an incident using the API.

### Part 7 — Explain the cloud path

Explain that Google Cloud infrastructure has been configured for the project, including Vertex AI and Firestore, while Cloud Run and Pub/Sub remain deployment steps rather than claiming they are already live.

---

## 11. Suggested evidence to capture

For a portfolio or technical demonstration, capture evidence of:

### Gemini

- terminal showing Gemini configuration
- successful `GeminiDecisionProvider` run
- selected workflow
- final `RESOLVED` state
- Gemini reasoning

### Tests

Show:

```text
32 passed
```

### API

Capture:

```text
GET /health
POST /incidents
GET /incidents
```

### Failure handling

Capture:

- retry behavior
- successful recovery
- escalation when retries are exhausted

### Google Cloud

Where useful, capture:

- WorkRelay project
- Vertex AI/API configuration
- Firestore database
- dedicated WorkRelay runtime service account
- billing budget/alerts

Never capture:

- access tokens
- private keys
- `.env` secrets
- credential files

---

## 12. Current deployment status

The demo must distinguish between **working locally**, **configured in Google Cloud**, and **deployed**.

### Working locally

- FastAPI API
- CLI runner
- Browser Operations Console
- Local decision provider
- Gemini decision provider
- deterministic workflows
- retry/recovery
- escalation
- lifecycle history
- local state store
- Firestore state store
- automated tests

### Deployed and verified on Google Cloud

- WorkRelay Cloud Run service
- Gemini 3.5 Flash through Google ADK
- Firestore incident persistence
- Artifact Registry container image
- dedicated WorkRelay runtime service account
- private Cloud Run access
- Cloud Run health endpoint
- end-to-end incident workflow

### Configured but not yet deployed/provisioned

- WorkRelay Cloud Run service
- Pub/Sub topics/subscriptions
- public production endpoint
- production observability configuration

Do not describe these future components as live infrastructure until they have actually been deployed and verified.

---

## 13. Demo safety and cost control

For normal development, prefer:

```bash
export WORKRELAY_DECISION_PROVIDER=local
export WORKRELAY_STATE_STORE=local
```

Switch to Gemini only when the real model behavior is being demonstrated or tested.

Avoid repeatedly running large numbers of Gemini requests just to test deterministic workflow behavior.

Similarly, use Firestore when cloud persistence itself needs to be demonstrated rather than for every local unit test.

---

## 14. Demo troubleshooting

### Gemini authentication error

Check:

```bash
gcloud auth application-default print-access-token
```

Then verify:

```bash
echo "$GOOGLE_CLOUD_PROJECT"
echo "$GOOGLE_CLOUD_LOCATION"
echo "$GOOGLE_GENAI_USE_ENTERPRISE"
```

Expected values for the current configuration:

```text
workrelay
global
TRUE
```

### Wrong provider selected

Check:

```bash
echo "$WORKRELAY_DECISION_PROVIDER"
```

Set explicitly:

```bash
export WORKRELAY_DECISION_PROVIDER=gemini
```

or:

```bash
export WORKRELAY_DECISION_PROVIDER=local
```

### Wrong state store

Check:

```bash
echo "$WORKRELAY_STATE_STORE"
```

Set explicitly:

```bash
export WORKRELAY_STATE_STORE=local
```

or:

```bash
export WORKRELAY_STATE_STORE=firestore
```

### API is not responding

Start the API:

```bash
uvicorn app.main:app --reload
```

Then:

```bash
curl http://127.0.0.1:8000/health
```

---

## 15. Demo conclusion

The strongest current WorkRelay demonstration is the real Gemini end-to-end flow:

```text
Operational incident
        ↓
Gemini 3.5 Flash
        ↓
Workflow decision
        ↓
Controlled workflow
        ↓
Remediation
        ↓
Verification
        ↓
RESOLVED
```

Combined with retry, escalation, lifecycle state, API access and Firestore support, this demonstrates the core agentic and cloud-native architecture without overstating the parts that have not yet been deployed.
