from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    app: str = Field("SQL Query Agent Environment", description="Application name")
    status: str = Field("running", description="Application status")
    message: str = Field(
        "SQL Query Agent Environment is running. Visit /docs for API reference.",
        description="Message for root endpoint",
    )


class HealthResponse(BaseModel):
    status: str = Field("ok", description="Health status")


class StateResponse(BaseModel):
    current_task_id: str = Field("task_1", description="Current active task")
    step_count: int = Field(0, description="Number of steps taken")
    episode_active: bool = Field(False, description="Whether episode is active")


class ResetRequest(BaseModel):
    task_id: str = Field("task_1", description="Task identifier for reset")


class StepRequest(BaseModel):
    query: str = Field("SELECT 1 as test;", description="SQL SELECT query")
    task_id: str = Field("task_1", description="Task ID for query context")


class Observation(BaseModel):
    task_id: str = Field("task_1", description="Active task")
    task_description: str = Field("", description="What the agent must accomplish")
    schema_info: dict[str, Any] = Field(default_factory=dict, description="Full database schema for reference")
    query_result: list[dict[str, Any]] = Field(default_factory=list, description="Rows returned by the agent's SQL query")
    error: Optional[str] = Field(default=None, description="SQL error message, if any")
    reward: float = Field(default=0.0, ge=0.0, le=1.0, description="Partial-credit score 0.0–1.0")
    done: bool = Field(default=False, description="Whether the episode has ended")
    feedback: Optional[str] = Field(default=None, description="Explanation of the reward awarded")
    step_count: int = Field(default=0, description="Steps taken so far this episode")


class SQLAction(StepRequest):
    pass


class SQLObservation(Observation):
    pass


class SQLState(BaseModel):
    episode_id: str = Field("episode_1", description="Unique episode identifier (UUID)")
    step_count: int = Field(default=0, description="Steps taken so far")
    current_task_id: str = Field(default="task_1", description="The task currently loaded")
    best_reward: float = Field(default=0.0, description="Highest reward achieved this episode")


# Alias for compatibility with app.py
Observation = SQLObservation

