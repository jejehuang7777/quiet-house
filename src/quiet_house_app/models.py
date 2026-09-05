from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Route = Literal["AUTO", "QUEUE", "HARD_GATE"]
DecisionSource = Literal["model_backed", "injected_deterministic"]


class RouteDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    route: Route
    reason: str = Field(min_length=1, max_length=500)
    interrupt_now: bool


class DecisionProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_kind: DecisionSource
    provider_id: str = Field(min_length=1, max_length=120)
    model_id: str | None = Field(default=None, min_length=1, max_length=120)
    generation_count: int = Field(ge=0, le=1)

    @model_validator(mode="after")
    def validate_source_claims(self) -> "DecisionProvenance":
        if self.source_kind == "model_backed":
            if self.model_id is None or self.generation_count != 1:
                raise ValueError("model-backed provenance requires a model id and one generation")
        elif self.model_id is not None or self.generation_count != 0:
            raise ValueError("injected provenance cannot claim a model or generation")
        return self


class DecisionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: RouteDecision
    provenance: DecisionProvenance


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
