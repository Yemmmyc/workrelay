# WorkRelay Development Guide

## Overview

This guide describes how to set up, test, run, and troubleshoot WorkRelay locally.

The project is designed so that most development and testing can be performed without Google Cloud usage. Google Cloud services are used when testing the Gemini decision provider or Firestore state persistence.

## Requirements

Recommended development environment:

- WSL Ubuntu
- Python 3.11+
- Google Cloud CLI (`gcloud`) for Google Cloud features
- Git
- Internet access for installing Python dependencies and accessing Google Cloud services when required

## Project location

The current project is developed in:

```bash
~/projects/workrelay
```

Change into the project:

```bash
cd ~/projects/workrelay
```

## Python virtual environment

Create the virtual environment if it does not already exist:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Verify Python:

```bash
python --version
```

The current development environment uses Python 3.11.

## Install dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

The main dependencies include:

- Pydantic
- Google ADK
- Google Gen AI
- Google Cloud Firestore
- FastAPI
- Uvicorn
- Jinja2 for the browser Operations Console
- pytest
- HTTP client support for API tests

## Environment configuration

WorkRelay uses environment variables to select its decision provider and state store.

The example configuration is stored in:

```text
.env.example
```

The default example is intentionally development-friendly:

```text
WORKRELAY_ENV=development
WORKRELAY_DECISION_PROVIDER=local
WORKRELAY_STATE_STORE=local
```

Gemini configuration is also documented there:

```text
GOOGLE_GENAI_USE_ENTERPRISE=TRUE
GOOGLE_CLOUD_PROJECT=workrelay
GOOGLE_CLOUD_LOCATION=global
```

The example file does not contain credentials or access tokens.

## Decision providers

### Local provider

Use the local provider for normal development and tests:

```bash
export WORKRELAY_DECISION_PROVIDER=local
```

The local provider is deterministic and does not require Google Cloud credentials.

### Gemini provider

Use Gemini when testing the real AI decision layer:

```bash
export WORKRELAY_DECISION_PROVIDER=gemini
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=workrelay
export GOOGLE_CLOUD_LOCATION=global
```

The Gemini provider uses Google ADK and Gemini 3.5 Flash through Google Cloud.

## Google authentication

For local Gemini or Firestore development, use Application Default Credentials.

Authenticate:

```bash
gcloud auth application-default login   --scopes=https://www.googleapis.com/auth/cloud-platform
```

Verify:

```bash
gcloud auth application-default print-access-token
```

A successful command should return an access token.

Do not save the access token in the repository.

Do not create or commit a service-account private key just for local development.

## State stores

### Local state

The local state store is the preferred option for routine development:

```bash
export WORKRELAY_STATE_STORE=local
```

It avoids cloud persistence and is appropriate for automated tests and deterministic local demonstrations.

### Firestore

Use Firestore when testing Google Cloud persistence:

```bash
export WORKRELAY_STATE_STORE=firestore
```

The current WorkRelay Firestore database is in:

```text
Google Cloud project: workrelay
Location: europe-west1
Database: (default)
```

The application uses the Firestore implementation through the `StateStore` abstraction and factory.

## Recommended development modes

### Lowest-cost local development

```bash
export WORKRELAY_DECISION_PROVIDER=local
export WORKRELAY_STATE_STORE=local
```

Use this for most tests and workflow development.

### Real Gemini, local state

```bash
export WORKRELAY_DECISION_PROVIDER=gemini
export WORKRELAY_STATE_STORE=local
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=workrelay
export GOOGLE_CLOUD_LOCATION=global
```

This is the preferred mode when specifically validating Gemini behavior without also requiring Firestore persistence.

### Gemini + Firestore

```bash
export WORKRELAY_DECISION_PROVIDER=gemini
export WORKRELAY_STATE_STORE=firestore
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=workrelay
export GOOGLE_CLOUD_LOCATION=global
```

Use this when testing the combined cloud-backed path.

## Run tests

From the project root:

```bash
pytest -q
```

The current test suite contains 34 tests, including Operations Console checks.

The latest verified result is:

```text
34 passed
```

Dependency deprecation warnings may appear. They are currently warnings from third-party packages and do not represent failed WorkRelay tests.

## Run the CLI

The command-line runner is:

```text
run.py
```

View available options:

```bash
python run.py --help
```

Example local run:

```bash
export WORKRELAY_DECISION_PROVIDER=local
export WORKRELAY_STATE_STORE=local

python run.py   --title "Payment API failure"   --description "Payment requests are failing."   --service payment-api   --severity high
```

Example Gemini run:

```bash
export WORKRELAY_DECISION_PROVIDER=gemini
export WORKRELAY_STATE_STORE=local
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=workrelay
export GOOGLE_CLOUD_LOCATION=global

python run.py   --title "Payment API failure"   --description "Payment requests are failing."   --service payment-api   --severity high
```

## Run the FastAPI application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API is available at:

```text
http://127.0.0.1:8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected:

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

Retrieve an incident:

```bash
curl http://127.0.0.1:8000/incidents/<INCIDENT_ID>
```

Replace `<INCIDENT_ID>` with the ID returned by the API.

## Browser Operations Console

The FastAPI application also serves the WorkRelay Operations Console. The UI is implemented with a Jinja2 HTML template and static CSS/JavaScript assets.

Project files:

```text
app/templates/index.html
app/static/style.css
```

Start the local console:

```bash
export WORKRELAY_DECISION_PROVIDER=local
export WORKRELAY_STATE_STORE=local

uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

The console calls the existing API endpoints rather than duplicating incident-processing logic. Incident creation therefore follows the same coordinator and workflow path as CLI and API clients.

For a real Gemini + Firestore UI test:

```bash
export WORKRELAY_DECISION_PROVIDER=gemini
export WORKRELAY_STATE_STORE=firestore
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=workrelay
export GOOGLE_CLOUD_LOCATION=global
```

The UI tests are included in `tests/test_api.py` and verify that the console and static CSS are served correctly.

## Application architecture during development

The application uses factories so the main application does not need to be rewritten when changing environments.

Decision provider:

```text
WORKRELAY_DECISION_PROVIDER
          |
          +---- local  -> LocalDecisionProvider
          |
          +---- gemini -> GeminiDecisionProvider
```

State store:

```text
WORKRELAY_STATE_STORE
          |
          +---- local     -> LocalStateStore
          |
          +---- firestore -> FirestoreStateStore
```

The coordinator receives these abstractions and executes the same workflow logic regardless of which implementation is selected.

## Failure-path testing

WorkRelay contains failure simulation options for testing retry and escalation behavior.

Inspect the supported options:

```bash
python run.py --help
```

Use the built-in simulation flags rather than intentionally breaking a real service.

The expected workflow pattern is:

```text
Failure
   |
   v
Retry
   |
   +---- recovery ---> RESOLVED
   |
   +---- failure ---> ESCALATED
```

## Code organization

The main application areas are:

```text
app/
├── agent/
│   ├── coordinator.py
│   ├── decision.py
│   ├── prompts.py
│   └── provider_factory.py
├── services/
│   ├── state_store.py
│   ├── state_store_interface.py
│   ├── state_store_factory.py
│   └── firestore_state_store.py
├── workflows/
│   ├── registry.py
│   └── incident_workflow.py
├── models/
│   └── incident.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── api.py
└── main.py
```

Tests are under:

```text
tests/
```

The CLI entry point is:

```text
run.py
```

## Development workflow

A recommended development cycle is:

### 1. Start in local mode

```bash
export WORKRELAY_DECISION_PROVIDER=local
export WORKRELAY_STATE_STORE=local
```

### 2. Make a small change

Keep changes focused and easy to review.

### 3. Run targeted tests

For example:

```bash
pytest tests/test_workflow.py -q
```

or:

```bash
pytest tests/test_api.py -q
```

### 4. Run the complete suite

```bash
pytest -q
```

### 5. Check the diff

```bash
git diff --check
```

Then review:

```bash
git diff
```

### 6. Check repository status

```bash
git status
```

### 7. Commit a coherent checkpoint

Use a clear commit message describing the change.

## Troubleshooting

### Gemini authentication problems

Check:

```bash
gcloud auth application-default print-access-token
```

Then verify the configuration:

```bash
echo "$WORKRELAY_DECISION_PROVIDER"
echo "$GOOGLE_GENAI_USE_ENTERPRISE"
echo "$GOOGLE_CLOUD_PROJECT"
echo "$GOOGLE_CLOUD_LOCATION"
```

For the current Gemini configuration, these should be:

```text
gemini
TRUE
workrelay
global
```

### Gemini model or location errors

The current configuration uses:

```text
GOOGLE_CLOUD_LOCATION=global
```

If changing the location, verify that the selected Gemini model is available through that endpoint before troubleshooting application code.

### Firestore errors

Verify:

```bash
echo "$WORKRELAY_STATE_STORE"
```

For Firestore testing:

```text
firestore
```

Also verify that Application Default Credentials are available.

### API does not start

Run:

```bash
uvicorn app.main:app --reload
```

If the port is already in use, identify the process using the port before starting another server.

### Tests unexpectedly call Gemini

Set:

```bash
export WORKRELAY_DECISION_PROVIDER=local
```

The automated suite should normally use controlled providers/mocks rather than repeatedly calling the live Gemini service.

## Dependency warnings

The current test run can display deprecation warnings from dependencies including Starlette/AnyIO, OpenTelemetry, Google ADK, and aiohttp.

These are not currently test failures.

Do not modify third-party packages inside `.venv` to suppress these warnings. Dependency upgrades can be evaluated separately.

## Security practices

Never commit:

- service-account private keys
- OAuth tokens
- Application Default Credential files
- production `.env` files
- API secrets
- passwords

Before committing:

```bash
git status
```

Review sensitive changes with:

```bash
git diff
```

For Google Cloud workloads, use the dedicated WorkRelay runtime service account rather than broad default credentials where appropriate.

## Cost-conscious development

Because Gemini and Google Cloud resources can incur usage:

- Use local decision mode for routine tests.
- Use local state for routine development.
- Run Gemini only when validating the real model integration.
- Use Firestore only when validating cloud persistence.
- Avoid repeated unnecessary end-to-end Gemini calls.
- Keep Cloud Run at zero/minimum usage when not needed during future deployment.
- Monitor billing and budget alerts.

## Before a release or deployment

Run:

```bash
pytest -q
git diff --check
git status
```

Then verify:

- README reflects the actual state.
- Documentation does not claim undeployed services are live.
- No secrets are committed.
- Gemini configuration is correct.
- State-store configuration is correct.
- Failure and retry behavior still works.
- Git history contains a clean, understandable checkpoint.

## Current development status

At the time of this documentation update:

- Local FastAPI API works.
- CLI runner works.
- Local decision provider works.
- Gemini decision provider works.
- Gemini 3.5 Flash has been successfully exercised end-to-end.
- Local state store works.
- Firestore state store is implemented.
- Retry and escalation paths are implemented.
- Lifecycle history is implemented.
- The automated suite has 34 passing tests.
- The browser Operations Console is implemented and locally verified.
- Google Cloud project infrastructure required for the current development path is configured.
- Cloud Run is deployed and the backend Gemini + Firestore path has been verified.
- The next deployment will include the Operations Console.
- Pub/Sub topics/subscriptions have not yet been provisioned.

This document should be updated as deployment architecture and operational practices evolve.
