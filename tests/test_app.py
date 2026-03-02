from fastapi.testclient import TestClient
import copy
import pytest

from src.app import app, activities

client = TestClient(app)

# keep a pristine copy for resets
_og_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: restore activities to original state before each test
    activities.clear()
    activities.update(copy.deepcopy(_og_activities))


def test_get_activities():
    # Arrange: none (reset fixture already ran)
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    assert resp.json() == _og_activities


def test_signup_new():
    # Arrange
    activity = "Chess Club"
    email = "alice@mergington.edu"
    # Act
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    existing = activities[activity]["participants"][0]
    # Act
    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    # Assert
    assert resp.status_code == 400


def test_signup_activity_not_found():
    # Arrange
    # Act
    resp = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
    # Assert
    assert resp.status_code == 404


def test_unregister_existing():
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    # Act
    resp = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_signed_up():
    # Arrange
    activity = "Chess Club"
    # Act
    resp = client.delete(f"/activities/{activity}/signup?email=not@mergington.edu")
    # Assert
    assert resp.status_code == 404


def test_unregister_activity_not_found():
    # Arrange
    # Act
    resp = client.delete("/activities/Nope/signup?email=test@mergington.edu")
    # Assert
    assert resp.status_code == 404
