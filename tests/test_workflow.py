from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from quiet_house_app.models import DecisionProvenance, DecisionResult, RouteDecision, SyntheticTask
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


def injected(decision: RouteDecision) -> DecisionResult:
    return DecisionResult(
        decision=decision,
        provenance=DecisionProvenance(
            source_kind="injected_deterministic",
            provider_id="unit_test_fixture",
            model_id=None,
            generation_count=0,
        ),
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
            summary = run_queue(tasks, root, decision_provider=lambda _: injected(next(decisions)))
            self.assertEqual(summary["status"], "PASS")
            self.assertEqual(summary["model_generation_count"], 0)
            self.assertEqual(len(list((root / "receipts").glob("*.json"))), 4)
            self.assertTrue((root / "workspace" / "auto-test-result.json").is_file())
            self.assertTrue((root / "queue" / "queue-test.json").is_file())
            self.assertFalse((root / "workspace" / "gate-now-test-result.json").exists())
            self.assertFalse((root / "workspace" / "gate-later-test-result.json").exists())
            persisted = json.loads((root / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(persisted, summary)
            for receipt_path in (root / "receipts").glob("*.json"):
                provenance = json.loads(receipt_path.read_text())["decision_provenance"]
                self.assertEqual(provenance["source_kind"], "injected_deterministic")
                self.assertIsNone(provenance["model_id"])
                self.assertEqual(provenance["generation_count"], 0)

    def test_receipts_are_immutable(self) -> None:
        fixed = RouteDecision(route="AUTO", reason="Authorized and reversible.", interrupt_now=False)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "smoke"
            run_queue([task("auto-test", "AUTO", False)], root, decision_provider=lambda _: injected(fixed))
            with self.assertRaises(FileExistsError):
                run_queue([task("auto-test", "AUTO", False)], root, decision_provider=lambda _: injected(fixed))

    def test_existing_output_root_fails_before_provider_without_mutation(self) -> None:
        calls = 0

        def provider(_: SyntheticTask) -> DecisionResult:
            nonlocal calls
            calls += 1
            return injected(RouteDecision(route="AUTO", reason="unused", interrupt_now=False))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "smoke"
            root.mkdir()
            marker = root / "existing.txt"
            marker.write_text("preserve me", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                run_queue([task("auto-test", "AUTO", False)], root, decision_provider=provider)
            self.assertEqual(calls, 0)
            self.assertEqual(list(root.iterdir()), [marker])
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve me")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "broken-output-link"
            root.symlink_to(Path(directory) / "missing-target", target_is_directory=True)
            with self.assertRaises(FileExistsError):
                run_queue([task("auto-test", "AUTO", False)], root, decision_provider=provider)
            self.assertEqual(calls, 0)
            self.assertTrue(root.is_symlink())

    def test_more_than_four_tasks_fail_before_provider_call(self) -> None:
        calls = 0

        def provider(_: SyntheticTask) -> DecisionResult:
            nonlocal calls
            calls += 1
            return injected(RouteDecision(route="AUTO", reason="unused", interrupt_now=False))

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "TASK_COUNT"):
                run_queue(
                    [task(f"case-{index}", "AUTO", False) for index in range(5)],
                    Path(directory) / "smoke",
                    decision_provider=provider,
                )
        self.assertEqual(calls, 0)

    def test_declared_model_backed_result_is_counted_without_model_call(self) -> None:
        result = DecisionResult(
            decision=RouteDecision(route="AUTO", reason="Declared result.", interrupt_now=False),
            provenance=DecisionProvenance(
                source_kind="model_backed",
                provider_id="test_model_adapter",
                model_id="synthetic-model-id",
                generation_count=1,
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            summary = run_queue(
                [task("model-declared", "AUTO", False)],
                Path(directory) / "smoke",
                decision_provider=lambda _: result,
            )
        self.assertEqual(summary["model_generation_count"], 1)

    def test_invalid_provenance_fails_before_any_output_write(self) -> None:
        invalid_results = [
            {"decision": {"route": "AUTO", "reason": "Missing provenance.", "interrupt_now": False}},
            {
                "decision": {"route": "AUTO", "reason": "Malformed provenance.", "interrupt_now": False},
                "provenance": {
                    "source_kind": "injected_deterministic",
                    "provider_id": "bad_fixture",
                    "model_id": None,
                    "generation_count": "not-an-integer",
                },
            },
            {
                "decision": {"route": "AUTO", "reason": "Contradictory provenance.", "interrupt_now": False},
                "provenance": {
                    "source_kind": "injected_deterministic",
                    "provider_id": "bad_fixture",
                    "model_id": "qwen3:14b",
                    "generation_count": 1,
                },
            },
        ]
        for invalid in invalid_results:
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / "smoke"
                with self.assertRaises(ValidationError):
                    run_queue([task("invalid", "AUTO", False)], root, decision_provider=lambda _: invalid)  # type: ignore[arg-type,return-value]
                self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()
