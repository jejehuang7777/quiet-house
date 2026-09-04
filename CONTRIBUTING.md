# Contributing

Quiet House is a bounded public alpha. Small, reviewable changes with synthetic evidence are preferred.

## Before opening a change

1. Do not include credentials, personal data, customer data, private local paths, or proprietary prompts.
2. Keep permission routing (`AUTO`, `QUEUE`, `HARD_GATE`) separate from interruption urgency (`interrupt_now`).
3. Add or update a no-model test for behavior changes.
4. Do not add external actions, automatic retries, provider fallback, deployment, or production claims without a separately reviewed design change.

## Local checks

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m compileall -q src tests
python -c "import quiet_house_app"
python -m unittest discover -s tests -v
quiet-house-smoke --help
```

These checks do not call Ollama. Running the optional smoke is not required for a pull request.

## Pull requests

Describe the problem, the smallest change, the synthetic evidence, and any boundary that remains untested. A passing test suite is not evidence of production reliability or comparative model performance.
