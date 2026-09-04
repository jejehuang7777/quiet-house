from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .agent import DecisionProvider, decide_with_strands
from .models import Outcome, RouteDecision, SyntheticTask


MAX_MODEL_GENERATIONS = 4


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _write_new(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(_canonical_json(value))
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def _execute(task: SyntheticTask, decision: RouteDecision, output_root: Path) -> Outcome:
    if decision.route == "AUTO":
        artifact = output_root / "workspace" / f"{task.task_id}-result.json"
        _write_new(
            artifact,
            {
                "synthetic": True,
                "task_id": task.task_id,
                "operation": "normalize_local_draft",
                "result": sorted(set(task.payload.get("items", []))),
            },
        )
        return Outcome(
            status="EXECUTED",
            detail="Completed one bounded reversible local transformation.",
            artifact=_relative(artifact, output_root),
        )
    if decision.route == "QUEUE":
        artifact = output_root / "queue" / f"{task.task_id}.json"
        _write_new(
            artifact,
            {
                "synthetic": True,
                "task_id": task.task_id,
                "queue": "next-bounded-review",
                "reason": "explicit deferral with no material loss",
            },
        )
        return Outcome(
            status="QUEUED",
            detail="Persisted one bounded queue record without interrupting the owner.",
            artifact=_relative(artifact, output_root),
        )
    return Outcome(
        status="STOPPED",
        detail=(
            "Stopped before the external commitment and requested immediate owner review."
            if decision.interrupt_now
            else "Stopped before the external commitment and deferred owner review to the normal window."
        ),
    )


def run_queue(
    tasks: Iterable[SyntheticTask],
    output_root: Path,
    *,
    decision_provider: DecisionProvider = decide_with_strands,
) -> dict[str, Any]:
    task_list = list(tasks)
    if not task_list or len(task_list) > MAX_MODEL_GENERATIONS:
        raise ValueError("TASK_COUNT_MUST_BE_BETWEEN_1_AND_4")
    if len({task.task_id for task in task_list}) != len(task_list):
        raise ValueError("TASK_IDS_MUST_BE_UNIQUE")

    output_root.mkdir(parents=True, exist_ok=False)
    receipt_summaries: list[dict[str, Any]] = []
    for index, task in enumerate(task_list, start=1):
        decision = decision_provider(task)
        outcome = _execute(task, decision, output_root)
        matched = (
            decision.route == task.expected_route
            and decision.interrupt_now == task.expected_interrupt_now
        )
        receipt = {
            "schema_version": "1.0",
            "synthetic": True,
            "sequence": index,
            "task": {
                "task_id": task.task_id,
                "title": task.title,
                "prompt_sha256": _sha256_text(task.prompt),
            },
            "agent_decision": decision.model_dump(),
            "expected": {
                "route": task.expected_route,
                "interrupt_now": task.expected_interrupt_now,
            },
            "decision_match": matched,
            "outcome": outcome.model_dump(),
            "model": {
                "provider": "local_ollama",
                "model_id": "qwen3:14b",
                "generation_number": index,
                "retry": 0,
                "reprompt": 0,
                "repair": 0,
                "model_switch": 0,
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "claim_ceiling": "local functional synthetic demo only",
        }
        receipt_path = output_root / "receipts" / f"{task.task_id}.json"
        _write_new(receipt_path, receipt)
        receipt_readback = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt_readback != receipt:
            raise RuntimeError("RECEIPT_READBACK_MISMATCH")
        receipt_summaries.append(
            {
                "task_id": task.task_id,
                "route": decision.route,
                "interrupt_now": decision.interrupt_now,
                "decision_match": matched,
                "outcome_status": outcome.status,
                "receipt": _relative(receipt_path, output_root),
                "receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
            }
        )

    summary = {
        "schema_version": "1.0",
        "synthetic": True,
        "status": "PASS" if all(item["decision_match"] for item in receipt_summaries) else "FAIL",
        "task_count": len(task_list),
        "model_generation_count": len(task_list),
        "retry_count": 0,
        "reprompt_count": 0,
        "repair_count": 0,
        "model_switch_count": 0,
        "receipts": receipt_summaries,
        "claim_ceiling": "local functional synthetic demo only",
    }
    _write_new(output_root / "summary.json", summary)
    return summary
