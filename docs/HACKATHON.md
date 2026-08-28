# WorkRelay Hackathon Notes

## Project

**WorkRelay — Automated Operational Incident Coordination System**

## Track

**The Taskmaster**

## Problem

Operational incidents require teams to understand the incident, select the correct response procedure, coordinate remediation, verify recovery, and escalate failures.

WorkRelay provides an automated coordination layer for this process.

## Solution

```text
Incident
   |
   v
Decision
   |
   v
Registered Workflow
   |
   v
Deterministic Execution
   |
   v
Verification
   |
   +--> Resolved
   |
   +--> Escalated
```

## Agentic component

Gemini + Google ADK provide the intelligent decision layer.

The model recommends the workflow rather than directly controlling operational actions.

This creates a clear boundary:

```text
Gemini reasoning
      |
      v
Workflow registry validation
      |
      v
Deterministic execution
```

## Implemented locally

- FastAPI incident intake
- Incident model and validation
- Decision-provider abstraction
- Local decision provider
- Gemini + Google ADK provider
- Gemini 3.5 Flash configuration
- Provider factory
- Workflow registry
- Deterministic workflow engine
- Investigation/remediation/verification
- Retry handling
- Escalation
- Local state persistence
- API tests
- Workflow tests
- Provider tests
- Application factory tests

Latest verified test result:

```text
25 passed
```

## Cloud status

The project is intentionally local-first while the requested $150 Google Cloud hackathon credit is pending.

Future cloud work is expected to include:

- Cloud Run
- Firestore
- Pub/Sub
- live Gemini execution

These are planned until actually deployed and tested.

## Submission honesty

The final submission should clearly distinguish:

### Verified

Local application behavior, tests, Gemini provider implementation and architecture.

### Pending

Live cloud deployment and cloud-service integration.

This avoids presenting planned infrastructure as completed infrastructure.

## Key technical message

> WorkRelay combines agent-assisted workflow selection with deterministic operational execution.

The important engineering decision is not simply adding a model. It is controlling where the model is allowed to influence the system.
