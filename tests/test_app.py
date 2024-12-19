import pytest
from fastapi.testclient import TestClient
from sf_spots_backend.app import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint returns correct response"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_workspaces():
    """Test the workspaces endpoint returns list of workspaces"""
    response = client.get("/workspaces")
    assert response.status_code == 200
    data = response.json()
    assert "workspaces" in data
    if "error" not in data:  # when database is configured
        workspaces = data["workspaces"]
        assert isinstance(workspaces, list)
        if workspaces:  # if there are workspaces
            workspace = workspaces[0]
            assert "id" in workspace
            assert "name" in workspace
            assert "address" in workspace
            assert "latitude" in workspace
            assert "longitude" in workspace
            assert "availableSpots" in workspace
            assert "totalSpots" in workspace

def test_get_workspace_occupancy():
    """Test the workspace occupancy endpoint returns correct data"""
    workspace_id = 1
    response = client.get(f"/workspace/{workspace_id}/occupancy")
    assert response.status_code == 200
    data = response.json()
    if "error" not in data:  # when database is configured
        assert "availableSpots" in data
        assert "totalSpots" in data
        assert isinstance(data["availableSpots"], int)
        assert isinstance(data["totalSpots"], int)
