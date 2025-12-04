import copy

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


import pytest


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict after each test to avoid cross-test pollution."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # There should be at least one activity and participants lists
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_creates_participant_and_reflects_in_list():
    activity = "Chess Club"
    email = "unittest@example.com"

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email in participants


def test_signup_existing_returns_400():
    activity = "Chess Club"
    existing = activities[activity]["participants"][0]

    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_participant_removes_from_list():
    activity = "Programming Class"
    email = activities[activity]["participants"][0]

    # Ensure exists
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert f"Unregistered {email}" in resp.json().get("message", "")

    # Verify removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    activity = "Programming Class"
    email = "doesnotexist@example.com"

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404
