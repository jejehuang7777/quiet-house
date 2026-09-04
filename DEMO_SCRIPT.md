# Five-minute demo script

## 0:00–0:35 — Problem

AI operators face two opposite failures: agents ask for permission on every harmless step, or they continue into actions that require human authority. Quiet House separates task routing from interruption timing and records every decision.

## 0:35–1:05 — Architecture

Show `docs/architecture.png`. A synthetic queue enters a Strands agent using a local model. The agent returns `AUTO`, `QUEUE`, or `HARD_GATE` plus `interrupt_now`. Deterministic code performs only the bounded local consequence and writes an immutable receipt.

## 1:05–1:30 — Start clean

Show the four synthetic cases in `examples/tasks.json`. From a fresh checkout, create and activate a virtual environment before installing the package.

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

Then run:

```bash
quiet-house-smoke --tasks examples/tasks.json --output artifacts/smoke
```

Explain that the command permits at most four generations and contains no retry, reprompt, repair, or model switch.

## 1:30–3:40 — Four live outcomes

1. `auto-001`: the agent recognizes explicit authority for a reversible local normalization; the executor writes a local result.
2. `queue-001`: the agent recognizes safe bounded deferral; the executor persists one queue item without interrupting the owner.
3. `gate-now-001`: the agent stops an unauthorized irreversible purchase and sets `interrupt_now=true` because the deadline would expire before normal review.
4. `gate-later-001`: the agent stops an unauthorized publication change but sets `interrupt_now=false` because waiting causes no material loss.

Open each receipt and point to the task hash, decision, expected boundary, deterministic outcome, and zero retry counters.

## 3:40–4:25 — Summary and safety

Open `artifacts/smoke/summary.json`. Confirm four unique receipts, the route distribution, and the distinction between stopping and interrupting. Emphasize that no real account, external action, customer data, or credential is involved.

## 4:25–5:00 — What this candidate proves

This alpha demonstrates that one installable local workflow can process four synthetic cases end to end with Strands decisions, deterministic consequences, receipts, and a local summary. It does not prove production reliability, statistical superiority, security certification, or deployment readiness.
