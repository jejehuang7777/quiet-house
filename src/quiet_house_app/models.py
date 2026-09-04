from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Route = Literal["AUTO", "QUEUE", "HARD_GATE"]


class RouteDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    route: Route
    reason: str = Field(min_length=1, max_length=500)
    interrupt_now: bool


class SyntheticTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(pattern=r"^[a-z0-9-]+$")
    title: str = Field(min_length=1, max_length=120)
    prompt: str = Field(min_length=1, max_length=2000)
    payload: dict[str, Any] = Field(default_factory=dict)
    expected_route: Route
    expected_interrupt_now: bool

    @model_validator(mode="after")
    def validate_expected_interrupt(self) -> "SyntheticTask":
        if self.expected_route != "HARD_GATE" and self.expected_interrupt_now:
            raise ValueError("only HARD_GATE may interrupt the owner")
        return self


class Outcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["EXECUTED", "QUEUED", "STOPPED"]
    detail: str
    artifact: str | None = None

