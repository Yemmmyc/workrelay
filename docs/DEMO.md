# WorkRelay Demo Guide

## 1. Activate the environment

```bash
cd ~/projects/workrelay
source .venv/bin/activate
```

## 2. Prove the tests

```bash
pytest -q
```

Current verified result:

```text
25 passed
```

## 3. Start the API

```bash
uvicorn app.main:app --reload
```

In another terminal:

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"healthy","service":"workrelay"}
```

## 4. Submit a HIGH incident

```bash
curl -X POST http://127.0.0.1:8000/incidents   -H "Content-Type: application/json"   -d '{
    "title": "Payment API failure",
    "description": "Payment requests are returning HTTP 500 errors.",
    "service": "payment-api",
    "severity": "HIGH"
  }'
```

Point out the selected workflow, status, reasoning and execution metadata.

## 5. Demonstrate retry

```bash
python run.py   --title "Temporary payment failure"   --description "Demonstrating recovery after a retry."   --service payment-api   --severity HIGH   --fail-remediation-once
```

Show the retry count and final resolution.

## 6. Demonstrate escalation

```bash
python run.py   --title "Critical service failure"   --description "Demonstrating controlled escalation."   --service core-api   --severity CRITICAL   --force-remediation-failure
```

Show that the critical workflow escalates without pretending the incident was resolved.

## 7. Explain the agentic boundary

Use this explanation:

> Gemini is responsible for recommending the appropriate registered workflow and providing reasoning. WorkRelay validates that recommendation, then deterministic application logic performs the operational workflow. The model does not directly execute arbitrary remediation.

## 8. Explain cloud status honestly

If credits are still pending:

> The local MVP and Gemini/ADK integration are implemented and tested. Cloud deployment is intentionally deferred until the required hackathon credits and credentials are available.

Do not claim Cloud Run, Firestore, Pub/Sub or live cloud Gemini execution is deployed until it has actually been tested.

## 9. Suggested presentation flow

1. Problem — operational incidents require coordination.
2. Architecture — decision layer separated from execution.
3. Live HIGH incident.
4. Retry demonstration.
5. Escalation demonstration.
6. Explain Gemini + ADK.
7. Explain cloud evolution.
