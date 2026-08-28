# WorkRelay Architecture

## Overview

WorkRelay separates incident decision-making from operational execution.

```text
Client
  |
  v
FastAPI
  |
  v
IncidentCoordinator
  |
  +--> DecisionProvider
  |       |
  |       +--> LocalDecisionProvider
  |       |
  |       +--> GeminiDecisionProvider
  |
  +--> Workflow Engine
          |
          +--> Investigation
          +--> Remediation
          +--> Verification
          +--> Retry / Escalation
  |
  v
LocalStateStore
```

## Application factory

`app/main.py` owns application composition through `create_app()`.

It creates:

1. FastAPI
2. State store
3. Configured decision provider
4. Incident coordinator
5. API routes

This keeps startup configuration separate from route definitions.

## API layer

`app/api.py` provides:

- `GET /health`
- `POST /incidents`
- `GET /incidents/{incident_id}`
- `GET /incidents`

Routes validate requests and delegate processing to the coordinator.

## Coordinator

`app/agent/coordinator.py` is the boundary between decision-making and execution.

It:

1. receives an incident
2. asks the decision provider for a workflow
3. records reasoning and provider metadata
4. persists the incident
5. starts the deterministic workflow

## Decision providers

`app/agent/decision.py` defines the provider abstraction.

### LocalDecisionProvider

A deterministic provider based on incident severity. It requires no external service.

### GeminiDecisionProvider

Uses Google ADK and Gemini 3.5 Flash to recommend a registered WorkRelay workflow.

Gemini returns structured data containing a workflow and reasoning.

The application rejects unknown workflows.

## Provider factory

`app/agent/provider_factory.py` reads:

```text
WORKRELAY_DECISION_PROVIDER
```

Supported values:

```text
local
gemini
```

Default:

```text
local
```

## Workflow registry

`app/workflows/registry.py` contains the allowed workflows.

Current workflows include:

- `standard_incident`
- `high_severity_incident`
- `critical_incident`

The registry prevents a model response from inventing an executable workflow.

## Deterministic workflow engine

`app/workflows/incident_workflow.py` owns execution.

A typical lifecycle is:

```text
Incident
   |
   v
Investigation
   |
   v
Remediation
   |
   +---- success ----> Verification ----> RESOLVED
   |
   +---- failure ----> Retry
                           |
                           +--> recover -> RESOLVED
                           |
                           +--> fail -> ESCALATED
```

## State management

The current local implementation uses `LocalStateStore` with JSON-backed persistence.

This service boundary is intended to make future migration to Firestore possible without redesigning workflow logic.

## Cloud target

When credits are available, the intended architecture is:

```text
Client
  |
  v
Cloud Run
  |
  v
WorkRelay Coordinator
  |
  +--> Gemini + ADK
  |
  +--> Workflow Engine
  |
  +--> Firestore
  |
  +--> Pub/Sub
```

This is target architecture, not a claim that those services are currently deployed.

## Design principles

- Deterministic execution
- Replaceable decision provider
- Validated model output
- Local-first development
- Isolated state persistence
- Testable components
- No secrets in source control
