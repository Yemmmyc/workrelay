# WorkRelay Development Guide

## Environment

Current development is local in WSL Ubuntu.

Project:

```text
~/projects/workrelay
```

Activate:

```bash
cd ~/projects/workrelay
source .venv/bin/activate
```

## Tests

```bash
pytest -q
```

Current checkpoint:

```text
25 passed
```

## Syntax checks

```bash
python -m py_compile app/api.py app/main.py tests/test_api.py
```

Whitespace check:

```bash
git diff --check
```

## Run API

```bash
uvicorn app.main:app --reload
```

## Provider configuration

Default:

```bash
WORKRELAY_DECISION_PROVIDER=local
```

Gemini:

```bash
WORKRELAY_DECISION_PROVIDER=gemini
```

Invalid provider names are rejected.

## Git workflow

Before committing:

```bash
git status
git diff --check
pytest -q
```

Then:

```bash
git add <files>
git commit -m "docs: update documentation"
```

Afterwards:

```bash
git status
```

The desired state is:

```text
nothing to commit, working tree clean
```

## Secrets

Never commit:

```text
.env
API keys
service-account keys
credentials
```

`.env.example` should contain only safe configuration examples.

## Local-first policy

Until cloud credits are available:

- keep routine development local
- use the local decision provider for ordinary tests
- avoid unnecessary cloud resources
- do not commit credentials
- test cloud components only when the required access exists

## Cloud migration

The intended sequence is:

```text
Local implementation
        |
        v
Automated tests
        |
        v
Credits approved
        |
        v
Google Cloud configuration
        |
        v
Live Gemini validation
        |
        v
Firestore / Pub/Sub
        |
        v
Cloud Run deployment
        |
        v
End-to-end cloud demo
```
