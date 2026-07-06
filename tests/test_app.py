from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_map():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()

    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_for_activity_success():
    activity_name = "Chess Club"
    email = "test-signup-success@mergington.edu"

    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]

    activities[activity_name]["participants"].remove(email)


def test_signup_for_activity_not_found():
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "missing-activity@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_duplicate_student():
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": existing_email}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_success():
    activity_name = "Chess Club"
    email = "test-unregister-success@mergington.edu"

    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_activity_not_found():
    response = client.delete(
        "/activities/Unknown%20Activity/participants",
        params={"email": "missing-activity@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_student_not_in_activity():
    activity_name = "Chess Club"
    email = "not-in-activity@mergington.edu"

    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in this activity"
