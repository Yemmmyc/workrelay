# WorkRelay Hackathon Context

## Original hackathon

WorkRelay was developed for the **Google All Things Agentic Hackathon** in the **The Taskmaster** track.

The original project goal was to demonstrate an agentic system that could receive an operational task, determine the appropriate response, carry out a multi-step workflow, handle failure, and reach a resolved or escalated outcome.

The hackathon submission period has now ended. This document is retained as historical project context and as a record of the original design goals.

## The Taskmaster concept

The WorkRelay concept was:

> An automated operational incident coordination system that receives an incident, determines the appropriate response workflow, executes the required actions, tracks state, verifies recovery, and resolves or escalates the incident.

The important distinction from a conventional chatbot was **action and orchestration**.

The intended flow was:

```text
Incident
   |
   v
Understand / classify
   |
   v
Select workflow
   |
   v
Execute multiple steps
   |
   v
Verify outcome
   |
   +---- success ---> RESOLVED
   |
   +---- failure ---> RETRY / ESCALATE
```

## Hackathon-aligned technology

The project was designed around the required Google agentic ecosystem:

```text
Gemini
   +
Google ADK
   +
Google Cloud infrastructure
```

The implemented decision layer uses:

- Gemini 3.5 Flash
- Google ADK
- Google Cloud / Vertex AI

The project also implements Google Cloud persistence through Firestore.

Cloud Run and Pub/Sub are part of the intended cloud architecture but are not currently represented as deployed WorkRelay services.

## What was actually implemented

The following capabilities were implemented and tested:

### Agentic decision layer

- Gemini 3.5 Flash decision provider
- Google ADK agent integration
- Structured coordination response
- Workflow selection based on incident context
- Validation of the selected workflow

### Controlled execution

- Workflow registry
- Deterministic incident workflow
- Investigation
- Remediation
- Verification
- Retry behavior
- Escalation behavior

### State and lifecycle

- Incident state model
- Local JSON-backed state store
- Firestore state store
- Lifecycle history
- Retry tracking
- Final resolution information

### Interfaces

- FastAPI API
- CLI incident runner
- Health endpoint
- Incident creation
- Incident listing
- Individual incident retrieval

### Engineering

- Provider abstraction
- Provider factory
- State-store abstraction
- State-store factory
- Automated test suite
- Local development mode
- Gemini integration tests

## Demonstrated Gemini workflow

A real end-to-end local demonstration was successfully completed using Gemini 3.5 Flash through Google ADK and Google Cloud.

The demonstrated incident was:

```text
Title    : Payment API failure
Service  : payment-api
Severity : HIGH
```

Gemini selected:

```text
high_severity_incident
```

The workflow completed with:

```text
Status       : RESOLVED
Current Step : incident_resolved
Retries      : 0
```

The result included Gemini coordination reasoning, investigation information, and verification information.

This is the strongest current evidence that the implemented agentic decision and deterministic execution path works end to end.

## Controlled autonomy

A central design decision was to avoid allowing the model to invent arbitrary operational commands.

Instead:

```text
Gemini
  |
  | recommends a workflow
  v
Workflow Registry
  |
  | validates approved workflow
  v
Deterministic execution
```

This provides a boundary between AI reasoning and operational execution.

The approach makes the system:

- easier to test
- easier to reason about
- more predictable
- safer to extend
- less dependent on unrestricted model-generated actions

## Failure handling

The project deliberately includes retry and escalation paths because an operational agent must handle failure.

The intended demonstration is:

```text
Incident
   |
   v
Workflow execution
   |
   +---- success ---> verification ---> RESOLVED
   |
   +---- temporary failure ---> RETRY
   |                              |
   |                              +---- recovered ---> RESOLVED
   |
   +---- persistent failure ---> ESCALATED
```

Failure simulation is built into the application so these paths can be demonstrated without intentionally disrupting a real production service.

## Google Cloud work completed

The WorkRelay Google Cloud project was configured for development and integration testing.

Configured components include:

- Google Cloud project `workrelay`
- Vertex AI API
- Firestore API
- Pub/Sub API
- Cloud Run API
- Artifact Registry API
- Cloud Build API
- Firestore Native database
- dedicated WorkRelay runtime service account

The Firestore database is configured in:

```text
europe-west1
```

The dedicated runtime service account is:

```text
workrelay-runtime@workrelay.iam.gserviceaccount.com
```

The runtime account has the application-required roles for Vertex AI and Firestore access.

## What was not deployed

The repository must not describe the following as live or deployed:

- WorkRelay Cloud Run service
- Pub/Sub topics/subscriptions
- public production endpoint
- production observability configuration

These remain future deployment steps.

The project documentation intentionally distinguishes:

```text
Implemented
Configured
Demonstrated
Deployed
```

These are not interchangeable terms.

## Credits and cost awareness

The original hackathon cloud-credit process was separate from the normal Google Cloud free-trial/developer benefits.

The project therefore avoided making deployment claims based only on the expectation of receiving hackathon credits.

For continued development, WorkRelay uses available Google Cloud development credits carefully.

Cost-conscious practices include:

- Gemini Flash rather than unnecessarily expensive models
- local decision mode for routine tests
- local state for routine development
- cloud services only when their behavior needs to be tested
- billing budget alerts
- avoiding unnecessary repeated Gemini calls

## Submission philosophy

The project was designed to demonstrate more than a conversational interface.

The key demonstration points were:

1. An operational incident enters the system.
2. An agentic decision is made.
3. A registered workflow is selected.
4. Multiple operational steps execute.
5. The result is verified.
6. Failure can trigger retry.
7. Persistent failure can trigger escalation.
8. State is recorded throughout the lifecycle.

This demonstrates autonomous coordination while keeping execution under application control.

## Original architecture intent

The intended cloud architecture was:

```text
Incident Source
      |
      v
Cloud Run
WorkRelay API
      |
      +--------------------+
      |                    |
      v                    v
Vertex AI / Gemini      Firestore
      |                 Incident State
      |
      v
   Pub/Sub
  Event-driven
    intake
```

The local implementation was built first so that the core workflow could be tested independently of cloud deployment.

This separation reduced unnecessary cloud usage while allowing the project to validate the agentic architecture before deployment.

## Current project status after the hackathon

The hackathon-specific submission period is complete, but WorkRelay remains a useful portfolio and cloud-native project.

Current implemented foundation:

```text
Gemini 3.5 Flash
       +
Google ADK
       +
FastAPI
       +
Operations Console
       +
Deterministic workflows
       +
Retry / escalation
       +
Lifecycle state
       +
Firestore support
       +
Cloud Run deployment
```

Post-hackathon status:

- The WorkRelay backend is deployed and verified on private Google Cloud Run.
- Gemini 3.5 Flash through Google ADK is verified in the deployed workflow.
- Firestore persistence is verified from the deployed service.
- The browser-based Operations Console is implemented and locally verified.
- The next Cloud Run revision will package the Operations Console into the deployed service.

Current next steps:

1. Deploy the Operations Console-enabled Cloud Run revision.
2. Add Pub/Sub event-driven intake.
3. Add production authentication and authorization.
4. Add structured observability.
5. Validate cloud failure/recovery behavior.
6. Replace simulated operational actions with real operational adapters.
7. Capture final deployment evidence for portfolio use.

## Documentation accuracy

This document intentionally records the difference between the original hackathon ambition and the current implementation.

When describing WorkRelay publicly:

### Safe claims

It is accurate to say that WorkRelay:

- uses Gemini 3.5 Flash
- uses Google ADK
- implements an agentic workflow
- performs controlled multi-step incident coordination
- supports retry and escalation
- supports local and Firestore state persistence
- has a FastAPI API and CLI
- has a browser-based Operations Console
- has been tested with a real Gemini end-to-end workflow
- has a verified private Cloud Run deployment
- persists deployed incident state in Firestore

### Claims to avoid until verified

Do not claim that WorkRelay currently:

- uses Pub/Sub in production
- has a public production endpoint
- has production-grade observability
- automatically handles real external production incidents
- provides production authentication and authorization

The current Cloud Run deployment is a private development/portfolio deployment rather than a public production service.

Those statements should only be added after the corresponding infrastructure is actually deployed and verified.

## Historical note

WorkRelay began as a hackathon project, but its architecture was intentionally designed so that it could continue beyond the competition.

The current goal is to turn the prototype into a credible portfolio demonstration of:

- agentic systems
- Google ADK
- Gemini
- cloud-native architecture
- controlled automation
- incident orchestration
- stateful workflows
- reliability engineering practices
