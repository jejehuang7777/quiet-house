# Quiet House

**Let your AI work—without letting it run wild.**

Quiet House is an early, local-first alpha that makes three workflow questions explicit:

1. May this task run automatically, wait in a queue, or must a person approve it?
2. If work must stop, does the operator need to be interrupted right now?
3. What evidence should remain after the decision?

It routes each synthetic task to `AUTO`, `QUEUE`, or `HARD_GATE`. In this alpha, `interrupt_now` refines a `HARD_GATE` by choosing immediate review or the normal review window. Every path records an immutable JSON receipt.

> This repository is a bounded public alpha. It uses synthetic examples only and is not a production deployment, security certification, or claim of statistical superiority.

## Understand it in 10 seconds

- `AUTO`: perform one predefined local action.
- `QUEUE`: record the task for later; do not interrupt.
- `HARD_GATE`: stop before the blocked action.
- `interrupt_now`: within `HARD_GATE`, choose immediate review (`true`) or the normal review window (`false`); `AUTO` and `QUEUE` use `false` in this alpha.
- every route produces a receipt and summary that can be inspected afterward.

## Understand it in 30 seconds

The included four-case synthetic smoke covers:

| Case | Route | Interrupt? | Expected behavior |
|---|---|---:|---|
| Authorized local work that should run now | `AUTO` | no | Execute the bounded local action and record it |
| Non-urgent authorized work | `QUEUE` | no | Save a queue item without doing the work |
| Urgent unauthorized work | `HARD_GATE` | yes | Stop and notify the operator |
| Non-urgent unauthorized work | `HARD_GATE` | no | Stop without an unnecessary interruption |

The route controls permission and outcome. For blocked work, `interrupt_now` controls when the person should review it: urgent `HARD_GATE` uses `true`; non-urgent `HARD_GATE` uses `false`.

## Understand it in 90 seconds

The alpha has two deliberately separate layers:

- a Strands/Ollama router that returns a structured decision for at most four synthetic tasks; and
- a deterministic executor that validates the decision, performs only the matching bounded local behavior, and writes receipts with exclusive-create semantics.

The no-model test suite injects fixed decisions, so the safety behavior can be checked without contacting Ollama. The model-backed smoke is optional, local-only, capped at one generation per task, and has no retry, repair, reprompt, or provider fallback. `HARD_GATE` never performs the requested blocked action.

See [the architecture diagram](docs/architecture.png), [the demo script](DEMO_SCRIPT.md), and [the limitations](DISCLOSURES.md).

## Requirements

- Python 3.11 or newer
- Ollama listening on `http://localhost:11434` for the optional model-backed smoke
- the local model tag `qwen3:14b` for that smoke

The install, import, CLI-help, and unit-test checks do not call a model.

## Install

Create and activate an isolated environment first.

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Run tests without a model

```bash
python3 -m unittest discover -s tests -v
```

These tests verify `AUTO`, `QUEUE`, `HARD_GATE`, receipt, and summary behavior with fixed decisions. They do not contact Ollama.

## Run the optional four-case local smoke

```bash
quiet-house-smoke --tasks examples/tasks.json --output artifacts/smoke
```

The command makes at most one local model generation per task and rejects task sets with more than four items. It does not retry, reprompt, repair, switch models, or perform external actions.

## Inspect the result

```bash
python3 -m json.tool artifacts/smoke/summary.json
python3 -m json.tool artifacts/smoke/receipts/auto-001.json
```

Receipts use exclusive-create semantics so a completed run cannot silently overwrite earlier evidence.

## Boundaries

- synthetic tasks only;
- local model only for the optional smoke;
- no external actions, real accounts, personal data, customer data, credentials, or deployment;
- `HARD_GATE` never performs the blocked action;
- `AUTO` and `QUEUE` use `interrupt_now=false`; urgent and non-urgent `HARD_GATE` cases use `true` and `false` respectively;
- accepted research artifacts are not runtime inputs to this alpha and are not modified;
- no adoption, production-reliability, security-certification, or comparative-performance claim is made.

## Package map

- `src/quiet_house_app/`: Strands routing and deterministic workflow
- `tests/`: no-model functional tests
- `examples/tasks.json`: four synthetic demo cases
- `docs/`: architecture source and rendered diagram
- `DEMO_SCRIPT.md`: five-minute demonstration plan
- `DISCLOSURES.md`: reuse and limitation disclosure
- `CONTRIBUTING.md`: contribution and local verification guide
- `SECURITY.md`: private vulnerability-reporting guidance
- `ROADMAP.md`: bounded alpha roadmap
- `CHANGELOG.md`: release history

## Project status

Quiet House is prerelease alpha software. The first versioned prerelease is `v0.1.0-alpha.1`; it does not represent a production deployment, security certification, comparative-performance result, or evidence of external adoption.
