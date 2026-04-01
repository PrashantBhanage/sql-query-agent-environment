"""Smoke tests for SQL Query Agent Environment."""
import pytest
from fastapi.testclient import TestClient


def test_app_imports():
    """Test that the app module imports correctly."""
    from server.app import app
    assert app is not None


def test_health_endpoint():
    """Test /health endpoint."""
    from server.app import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_root_endpoint():
    """Test / endpoint."""
    from server.app import app
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert data["status"] == "running"


def test_state_endpoint():
    """Test /state endpoint."""
    from server.app import app
    client = TestClient(app)
    response = client.get("/state")
    assert response.status_code == 200
    data = response.json()
    assert "current_task_id" in data
    assert "step_count" in data


def test_reset_endpoint():
    """Test /reset endpoint."""
    from server.app import app
    client = TestClient(app)
    response = client.post("/reset", json={"task_id": "task_1"})
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "task_1"
    assert data["step_count"] == 0
    assert "schema_info" in data


def test_step_endpoint():
    """Test /step endpoint with valid query."""
    from server.app import app
    client = TestClient(app)
    
    # Reset first
    client.post("/reset", json={"task_id": "task_1"})
    
    # Execute query
    response = client.post("/step", json={
        "query": "SELECT 1 as test;",
        "task_id": "task_1"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "task_1"
    assert "query_result" in data


def test_step_endpoint_rejects_non_select():
    """Test that /step endpoint rejects non-SELECT queries."""
    from server.app import app
    client = TestClient(app)
    
    # Reset first
    client.post("/reset", json={"task_id": "task_1"})
    
    # Try INSERT
    response = client.post("/step", json={
        "query": "INSERT INTO customers (name) VALUES ('test');",
        "task_id": "task_1"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["error"] is not None


def test_inference_import():
    """Test that inference module imports correctly."""
    from inference import SQLQueryAgent, create_agent
    agent = create_agent()
    assert agent is not None


def test_baseline_import():
    """Test that baseline_inference module imports correctly."""
    from baseline_inference import BaselineAgent, create_baseline_agent
    agent = create_baseline_agent()
    assert agent is not None
