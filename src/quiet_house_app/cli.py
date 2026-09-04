from __future__ import annotations

import argparse
import json
from pathlib import Path

from pydantic import TypeAdapter

from .models import SyntheticTask
from .workflow import run_queue


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Quiet House synthetic demo")
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    raw = json.loads(args.tasks.read_text(encoding="utf-8"))
    tasks = TypeAdapter(list[SyntheticTask]).validate_python(raw)
    summary = run_queue(tasks, args.output)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
