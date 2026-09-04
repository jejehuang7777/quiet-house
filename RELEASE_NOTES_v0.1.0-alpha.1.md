# Quiet House v0.1.0-alpha.1

Quiet House v0.1.0-alpha.1 is a local-first, synthetic-only prerelease for separating what an AI-assisted workflow may do from when it should interrupt a person.

The bundled four-case demo routes tasks to `AUTO`, `QUEUE`, or `HARD_GATE`. `AUTO` and `QUEUE` use `interrupt_now=false`; within `HARD_GATE`, `interrupt_now` chooses immediate review (`true`) or the normal review window (`false`). Every path writes an immutable JSON receipt.

No-model tests cover the deterministic workflow. The optional local Strands/Ollama smoke is capped at one generation per task, with no retry, reprompt, repair, model switch, or provider fallback.

This prerelease is not a production deployment, security certification, comparative-performance claim, or evidence of external adoption. It performs no real external actions and accepts no real accounts, personal data, customer data, or credentials.
