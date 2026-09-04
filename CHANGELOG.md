# Changelog

All notable changes to this project will be documented here.

## [Unreleased]

- No changes yet.

## [0.1.0-alpha.1] - 2026-09-04

- Added structured `AUTO`, `QUEUE`, and `HARD_GATE` routing for four synthetic task cases.
- Defined route as the permission/outcome control. In the bundled alpha, `AUTO` and `QUEUE` use `interrupt_now=false`; within `HARD_GATE`, `interrupt_now` selects immediate versus normal-window review.
- Added deterministic bounded execution, queueing, hard-gate stops, immutable JSON receipts, and a local summary.
- Added no-model functional tests and an optional capped local Strands/Ollama smoke.
- Added public-maintainer documentation, issue templates, and no-model CI configuration.

[Unreleased]: https://github.com/jejehuang7777/quiet-house/compare/v0.1.0-alpha.1...HEAD
[0.1.0-alpha.1]: https://github.com/jejehuang7777/quiet-house/releases/tag/v0.1.0-alpha.1

This release is a bounded public alpha, not a production deployment, security certification, comparative-performance result, or evidence of external adoption.
