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
    current_task_id: str = Field(..., description="Current active task")
    step_count: int = Field(..., description="Number of steps taken")
    episode_active: bool = Field(..., description="Whether episode is active")


class ResetRequest(BaseModel):
    task_id: str = Field(..., description="Task identifier for reset")


class StepRequest(BaseModel):
    query: str = Field(..., description="SQL SELECT query")
    task_id: str = Field(..., description="Task ID for query context")


class Observation(BaseModel):
    task_id: str = Field(..., description="Active task")
    task_description: str = Field(..., description="What the agent must accomplish")
    schema_info: dict[str, Any] = Field(..., description="Full database schema for reference")
    query_result: list[dict[str, Any]] = Field(default_factory=list, description="Rows returned by the agent's SQL query")
    error: Optional[str] = Field(default=None, description="SQL error message, if any")
    reward: float = Field(default=0.0, ge=0.0, le=1.0, description="Partial-credit score 0.0–1.0")
    done: bool = Field(default=False, description="Whether the episode has ended")
    feedback: Optional[str] = Field(default=None, description="Explanation of the reward awarded")
    step_count: int = Field(default=0, description="Steps taken so far this episode")


# kept for compatibility with existing naming
class SQLAction(StepRequest):
    pass


class SQLObservation(Observation):
    pass


class SQLState(BaseModel):
    episode_id: str = Field(..., description="Unique episode identifier (UUID)")
    step_count: int = Field(default=0, description="Steps taken so far")
    current_task_id: str = Field(default="task_1", description="The task currently loaded")
    best_reward: float = Field(default=0.0, description="Highest reward achieved this episode")


# API Request/Response models for FastAPI app

class RootResponse(BaseModel):
    """Root endpoint response."""
    message: str = Field(
        default="SQL Query Agent Environment is running. Visit /docs for API reference.",
        description="Welcome message for the API."
    )


class HealthResponse(BaseModel):
    """Health check endpoint response."""
    status: str = Field(default="ok", description="Health status of the service.")


class StateResponse(BaseModel):
    """Current environment state response."""
    current_task_id: str = Field(default="task_1", description="The task currently loaded.")
    step_count: int = Field(default=0, description="Steps taken so far this episode.")
    episode_active: bool = Field(default=False, description="Whether an episode is currently active.")


class ResetRequest(BaseModel):
    """Request to reset the environment for a new task."""
    task_id: str = Field("task_1", description="Task identifier to reset to: 'task_1', 'task_2', etc.")


class StepRequest(BaseModel):
    """Request to execute a step in the environment."""
    query: str = Field(..., description="SQL SELECT statement to execute.")
    task_id: str = Field("task_1", description="Task identifier for the current task.")


# Alias for compatibility with app.py
Observation = SQLObservation
