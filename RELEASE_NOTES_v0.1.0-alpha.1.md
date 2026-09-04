# Quiet House v0.1.0-alpha.1 — draft release notes

Quiet House is a local-first, synthetic-only alpha for separating what an AI-assisted workflow may do from when it should interrupt a person.

The four-case demo routes tasks to `AUTO`, `QUEUE`, or `HARD_GATE`, keeps `interrupt_now` independent from that route, and writes immutable JSON receipts. No-model tests cover the deterministic workflow; an optional Strands/Ollama smoke is capped at one generation per task with no retry or provider fallback.

This alpha is not a production deployment, security certification, or comparative-performance claim. It performs no real external actions and accepts no real accounts, personal data, customer data, or credentials.

These notes are a public draft for the planned tag. The tag and GitHub release do not exist yet.
