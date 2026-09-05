# WorkRelay Architecture

## Overview

WorkRelay is an automated operational incident coordination system designed around a controlled agentic workflow.

The system separates **AI-assisted decision-making** from **deterministic operational execution**:

> **Gemini recommends the workflow; deterministic application logic executes it.**

This separation allows the decision layer to use an LLM while keeping operational actions constrained to workflows explicitly registered by the application.

## High-level architecture

```text
                         +----------------------+
                         |      Incident        |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         |    FastAPI / CLI      |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | IncidentCoordinator  |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         |  Decision Provider   |
                         +----------+-----------+
                                    |
                    +---------------+---------------+
                    |                               |
          +---------v---------+           +---------v---------+
          |  Local Provider   |           |   Gemini + ADK   |
          |  deterministic    |           | Gemini 3.5 Flash |
          +---------+---------+           +---------+---------+
                    |                               |
                    +---------------+---------------+
                                    |
                         +----------v-----------+
                         |  Workflow Registry   |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Deterministic        |
                         | Incident Workflow    |
                         +----------+-----------+
                                    |
                         +----------+-----------+
                         |                      |
                  +------v------+        +------v------+
                  | Remediation |        | Verification|
                  +------+------+        +------+------+
                         |                      |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Resolved / Escalated |
                         +----------------------+
                                    |
                         +----------v-----------+
                         |     State Store      |
                         +----------+-----------+
                                    |
                         +----------+-----------+
                         | Local JSON /         |
                         | Firestore            |
                         +----------------------+
```

## Main components

### 1. FastAPI, Operations Console and CLI interfaces

WorkRelay exposes three interface layers for interacting with incidents:

- Browser-based Operations Console
- FastAPI HTTP API
- `run.py` command-line runner

The Operations Console is a human-facing web interface served directly by the FastAPI application. It provides incident intake, operational status visibility, recent-incident review, and detailed lifecycle inspection.

The browser console does not make workflow decisions itself. It submits incidents to the same FastAPI API used by programmatic clients and the CLI, ensuring that all incidents pass through the same coordinator, decision-provider abstraction, deterministic workflow engine, and state store.

The API currently provides:

- `GET /` — Operations Console
- `GET /health`
- `POST /incidents`
- `GET /incidents`
- `GET /incidents/{incident_id}`
- `/static/*` — browser UI assets

The CLI is useful for reproducible local demonstrations and failure-path testing.

The interface architecture is therefore:

```text
                    +----------------------+
                    |       Browser        |
                    +----------+-----------+
                               |
                               v
                    +----------+-----------+
                    | Operations Console   |
                    | HTML / CSS / JS      |
                    +----------+-----------+
                               |
                               v
                    +----------+-----------+
                    |      FastAPI         |
                    +----------+-----------+
                               |
                    +----------+-----------+
                    | IncidentCoordinator  |
                    +----------+-----------+
                               |
                         Decision Provider
```

All three interfaces ultimately use the same application coordination and workflow execution path.

## 2. Incident model

The incident model contains the operational context needed by the coordinator and decision provider, including:

- incident ID
- title
- description
- service
- severity
- status
- current workflow step
- retry information
- resolution information
- metadata
- lifecycle history

The model is defined using Pydantic and provides validation at the application boundary.

## 3. IncidentCoordinator

`IncidentCoordinator` is the central orchestration component.

Its responsibilities include:

1. Accepting an incident.
2. Persisting the incident state.
3. Asking the configured decision provider to select a workflow.
4. Validating the selected workflow against the workflow registry.
5. Executing the selected workflow.
6. Handling retries and escalation.
7. Recording lifecycle changes.
8. Persisting the final incident state.

The coordinator does not need to know whether the decision came from the local provider or Gemini. This is achieved through the `DecisionProvider` abstraction.

## 4. Decision provider abstraction

WorkRelay defines a decision-provider interface so that the intelligence layer can be changed without changing the workflow engine.

```text
DecisionProvider
       |
       +---- LocalDecisionProvider
       |
       +---- GeminiDecisionProvider
```

### LocalDecisionProvider

The local provider makes deterministic decisions based on the application's rules.

It is useful for:

- unit tests
- development without cloud credentials
- deterministic demonstrations
- low-cost development

### GeminiDecisionProvider

The Gemini provider uses:

- Google ADK
- Gemini 3.5 Flash
- Google Cloud / Vertex AI
- structured output validation

The provider sends controlled incident context to Gemini and asks it to select one of the application's supported workflows.

Gemini's output is validated before execution.

The model is therefore used as a **decision layer**, not as an unrestricted execution engine.

## 5. Gemini + Google ADK flow

The Gemini provider creates an ADK agent configured for workflow selection.

Conceptually:

```text
Incident context
      |
      v
GeminiDecisionProvider
      |
      v
Google ADK Agent
      |
      v
Gemini 3.5 Flash
      |
      v
Structured coordination response
      |
      v
Workflow validation
      |
      v
IncidentCoordinator
```

The current local configuration uses:

```text
GOOGLE_GENAI_USE_ENTERPRISE=TRUE
GOOGLE_CLOUD_PROJECT=workrelay
GOOGLE_CLOUD_LOCATION=global
```

The global location is used for the current Gemini configuration because the model is available through that endpoint.

For local development, Google Application Default Credentials are used rather than storing service-account private keys in the repository.

## 6. Workflow Registry

The workflow registry contains the workflows that WorkRelay is allowed to execute.

The decision provider selects from these registered workflows rather than generating arbitrary operational procedures.

This creates a safety boundary:

```text
LLM decision
     |
     v
Approved workflow name
     |
     v
Workflow Registry
     |
     +---- valid --> execute
     |
     +---- invalid -> reject
```

This approach keeps the execution surface controlled and testable.

## 7. Deterministic incident workflow

`IncidentWorkflow` performs the operational sequence selected by the coordinator.

The workflow can include:

```text
Investigate
    |
    v
Remediate
    |
    v
Verify
    |
    +---- success ---> RESOLVED
    |
    +---- failure ---> Retry
                         |
                         +---- recovery ---> RESOLVED
                         |
                         +---- exhausted -> ESCALATED
```

The workflow supports simulated failures so retry and escalation behavior can be tested without deliberately causing a real service outage.

## 8. Retry and escalation

WorkRelay treats failure handling as part of the workflow rather than as an afterthought.

A failed operation can:

1. Record the failure.
2. Increment the retry count.
3. Retry according to the configured workflow behavior.
4. Verify recovery.
5. Resolve the incident if recovery succeeds.
6. Escalate when recovery cannot be completed.

This allows the system to demonstrate autonomous multi-step behavior rather than simply returning a text response.

## 9. State management

State persistence is abstracted behind the `StateStore` interface.

```text
StateStore
    |
    +---- LocalStateStore
    |
    +---- FirestoreStateStore
```

### Local state

The local store is intended for development and testing.

It provides a simple JSON-backed persistence mechanism.

### Firestore

The Firestore implementation uses Google Cloud Firestore for persistent incident state.

The current Google Cloud project contains a Firestore Native database in:

```text
europe-west1
```

The application can select the Firestore implementation with:

```bash
export WORKRELAY_STATE_STORE=firestore
```

The dedicated runtime service account is:

```text
workrelay-runtime@workrelay.iam.gserviceaccount.com
```

and has the application-required Google Cloud roles for Firestore and Vertex AI access.

## 10. Configuration factories

WorkRelay uses factories to keep environment-specific choices outside the core orchestration logic.

### Decision provider factory

```text
WORKRELAY_DECISION_PROVIDER=local
```

or:

```text
WORKRELAY_DECISION_PROVIDER=gemini
```

### State store factory

```text
WORKRELAY_STATE_STORE=local
```

or:

```text
WORKRELAY_STATE_STORE=firestore
```

This makes it possible to develop locally while retaining a clear path to Google Cloud deployment.

## 11. Google Cloud architecture

The current cloud architecture is:

```text
                    +------------------+
                    | External / API   |
                    | Incident Source  |
                    +--------+---------+
                             |
                             v
                    +--------+---------+
                    |    Cloud Run     |
                    |    WorkRelay     |
                    +--------+---------+
                             |
                +------------+-------------+
                |                          |
                v                          v
        +-------+--------+          +------+-------+
        | Vertex AI /    |          |  Firestore   |
        | Gemini 3.5     |          | Incident     |
        | Flash          |          | State        |
        +----------------+          +--------------+
                |
                |
                v
        +-------+--------+
        |    Pub/Sub     |
        | event intake / |
        | future async   |
        +----------------+
```

### Current cloud status

#### Deployed and verified

- Google Cloud project `workrelay`
- Cloud Run service `workrelay`
- Artifact Registry WorkRelay container image
- Gemini 3.5 Flash through Google ADK / Vertex AI
- Firestore Native database
- Dedicated WorkRelay runtime service account
- Private Cloud Run access
- Scale-to-zero configuration with maximum one instance
- End-to-end Cloud Run → Gemini → Firestore incident workflow

#### Implemented locally and pending deployment

- Browser-based Operations Console
- HTML template and static CSS assets
- UI incident intake and recent-incident visibility
- Detailed incident lifecycle modal

The next deployment step is to rebuild the container and deploy a new Cloud Run revision containing the Operations Console.

#### Not yet deployed/provisioned

- Pub/Sub topics and subscriptions
- production observability stack
- public production endpoint
- production authentication and authorization

The architecture document intentionally distinguishes **deployed infrastructure** from **implemented locally** and **future infrastructure**.

## 12. Security model

The current design avoids embedding cloud credentials in application code.

Local development uses Application Default Credentials.

Cloud deployment should use the dedicated runtime service account:

```text
workrelay-runtime@workrelay.iam.gserviceaccount.com
```

with least-privilege application roles.

The repository should never contain:

- service-account private keys
- access tokens
- API secrets
- local credential files
- production `.env` files

Before production exposure, the API should also gain authentication and authorization, along with stronger request controls and production secret management.

## 13. Reliability and observability

The architecture is designed to make failure states explicit.

Important state transitions include:

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
   +----> RESOLVED
   |
   +----> RETRYING
             |
             +----> RESOLVED
             |
             +----> ESCALATED
```

Lifecycle history provides an audit trail of state changes.

For production deployment, the next observability improvements should include:

- structured application logs
- Cloud Logging integration
- metrics
- alerting
- correlation/request IDs
- visibility into workflow duration, retries, failures and escalations

## 14. Testing strategy

WorkRelay is designed to test the decision and execution layers separately.

Tests cover areas including:

- workflow selection
- state-store operations
- incident lifecycle
- successful resolution
- retry and recovery
- escalation
- API behavior
- decision-provider behavior
- Gemini provider behavior through controlled tests

The current local test suite contains **32 passing tests**.

A real Gemini end-to-end test has also been successfully run locally using Gemini 3.5 Flash through Google Cloud.

## 15. Design principles

### Controlled autonomy

The model can make a decision, but execution is constrained by application-defined workflows.

### Separation of concerns

The decision layer, coordinator, workflow engine, persistence layer and interfaces have separate responsibilities.

### Provider independence

The system can run without Gemini by using the local decision provider.

### Persistence independence

The system can use local state during development and Firestore when Google Cloud persistence is required.

### Failure-aware execution

Retries, verification and escalation are first-class workflow behavior.

### Reproducibility

The CLI, test suite and documented configuration provide a repeatable development and demonstration path.

## 16. Future evolution

The current architecture has already been deployed and verified on Google Cloud with:

- Cloud Run
- Gemini 3.5 Flash through Google ADK
- Firestore persistence
- Artifact Registry
- Dedicated WorkRelay runtime service account

The browser-based Operations Console is implemented and has been verified locally against the same FastAPI application. The next deployment step is to rebuild the container and deploy a new Cloud Run revision containing the web UI.

Future architectural evolution includes:

1. Introduce Pub/Sub for event-driven incident intake.
2. Add production authentication and authorization.
3. Add structured observability and alerting.
4. Validate cloud-native failure and recovery scenarios.
5. Add stronger operational controls around retries, idempotency and concurrent incidents.
6. Replace deterministic simulated operational actions with pluggable integrations for real logs, metrics, traces, health checks, and remediation systems.

The architecture intentionally keeps these future capabilities behind explicit application boundaries so that additional automation can be introduced without giving the decision layer unrestricted operational control.
