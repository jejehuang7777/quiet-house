from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from quiet_house_app.models import RouteDecision, SyntheticTask
from quiet_house_app.workflow import run_queue


def task(task_id: str, route: str, interrupt: bool) -> SyntheticTask:
    return SyntheticTask(
        task_id=task_id,
        title=f"Synthetic {route}",
        prompt=f"Synthetic prompt for {route}",
        payload={"items": ["beta", "alpha", "beta"]},
        expected_route=route,
        expected_interrupt_now=interrupt,
    )


class WorkflowTests(unittest.TestCase):
    def test_four_paths_create_receipts_and_summary(self) -> None:
        tasks = [
            task("auto-test", "AUTO", False),
            task("queue-test", "QUEUE", False),
            task("gate-now-test", "HARD_GATE", True),
            task("gate-later-test", "HARD_GATE", False),
        ]
        decisions = iter(
            [
                RouteDecision(route="AUTO", reason="Authorized and reversible.", interrupt_now=False),
                RouteDecision(route="QUEUE", reason="Bounded deferral is preferred.", interrupt_now=False),
                RouteDecision(route="HARD_GATE", reason="Deadline requires owner authority now.", interrupt_now=True),
                RouteDecision(route="HARD_GATE", reason="Owner authority is needed at normal review.", interrupt_now=False),
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "smoke"
            summary = run_queue(tasks, root, decision_provider=lambda _: next(decisions))
            self.assertEqual(summary["status"], "PASS")
            self.assertEqual(summary["model_generation_count"], 4)
            self.assertEqual(len(list((root / "receipts").glob("*.json"))), 4)
            self.assertTrue((root / "workspace" / "auto-test-result.json").is_file())
            self.assertTrue((root / "queue" / "queue-test.json").is_file())
            self.assertFalse((root / "workspace" / "gate-now-test-result.json").exists())
            self.assertFalse((root / "workspace" / "gate-later-test-result.json").exists())
            persisted = json.loads((root / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(persisted, summary)

    def test_receipts_are_immutable(self) -> None:
        fixed = RouteDecision(route="AUTO", reason="Authorized and reversible.", interrupt_now=False)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "smoke"
            run_queue([task("auto-test", "AUTO", False)], root, decision_provider=lambda _: fixed)
            with self.assertRaises(FileExistsError):
                run_queue([task("auto-test", "AUTO", False)], root, decision_provider=lambda _: fixed)

    def test_more_than_four_tasks_fail_before_provider_call(self) -> None:
        calls = 0

        def provider(_: SyntheticTask) -> RouteDecision:
            nonlocal calls
            calls += 1
            return RouteDecision(route="AUTO", reason="unused", interrupt_now=False)

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "TASK_COUNT"):
                run_queue(
                    [task(f"case-{index}", "AUTO", False) for index in range(5)],
                    Path(directory) / "smoke",
                    decision_provider=provider,
                )
        self.assertEqual(calls, 0)


if __name__ == "__main__":
    unittest.main()

