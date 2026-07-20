import pytest


# ============================================================================
# Test: Get all activities
# ============================================================================
def test_get_activities(client):
    """Test retrieving all activities"""
    # Arrange
    expected_activities = {"Chess Club", "Programming Class", "Gym Class"}
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    for activity in expected_activities:
        assert activity in data


def test_activity_structure(client):
    """Test that activities have correct structure"""
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}
    
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    for activity_name, details in activities.items():
        assert all(field in details for field in required_fields)
        assert isinstance(details["participants"], list)
        assert isinstance(details["max_participants"], int)


# ============================================================================
# Test: Signup functionality
# ============================================================================
def test_signup_new_participant(client):
    """Test signing up a new participant"""
    # Arrange
    email = "newstudent@example.com"
    activity = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    assert f"Signed up {email}" in response.json()["message"]


def test_signup_duplicate_participant(client):
    """Test that duplicate signups are rejected"""
    # Arrange
    email = "duplicate@example.com"
    activity = "Chess Club"
    
    # Act - First signup
    response1 = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert - First signup succeeds
    assert response1.status_code == 200
    
    # Act - Second signup (duplicate)
    response2 = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert - Second signup fails
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_nonexistent_activity(client):
    """Test signup to a non-existent activity"""
    # Arrange
    email = "test@example.com"
    activity = "Nonexistent Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_participant_count_increases_after_signup(client):
    """Test that participant count updates after successful signup"""
    # Arrange
    email = "counter@example.com"
    activity = "Programming Class"
    
    # Act - Get initial count
    response_before = client.get("/activities")
    initial_count = len(response_before.json()[activity]["participants"])
    
    # Act - Sign up
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Act - Get new count
    response_after = client.get("/activities")
    new_count = len(response_after.json()[activity]["participants"])
    
    # Assert
    assert new_count == initial_count + 1
    assert email in response_after.json()[activity]["participants"]


# ============================================================================
# Test: Removal functionality
# ============================================================================
def test_remove_participant(client):
    """Test removing a participant from an activity"""
    # Arrange
    email = "remove@example.com"
    activity = "Chess Club"
    
    # Act - Sign up first
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Act - Remove
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]


def test_remove_nonexistent_participant(client):
    """Test removing a participant who isn't signed up"""
    # Arrange
    email = "notregistered@example.com"
    activity = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_remove_from_nonexistent_activity(client):
    """Test removing from a non-existent activity"""
    # Arrange
    email = "test@example.com"
    activity = "Fake Club"
    
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_participant_count_decreases_after_removal(client):
    """Test that participant count updates after removal"""
    # Arrange
    email = "counter2@example.com"
    activity = "Gym Class"
    
    # Act - Sign up
    client.post(f"/activities/{activity}/signup?email={email}")
    response_before = client.get("/activities")
    count_after_signup = len(response_before.json()[activity]["participants"])
    
    # Act - Remove
    client.delete(f"/activities/{activity}/signup?email={email}")
    response_after = client.get("/activities")
    count_after_removal = len(response_after.json()[activity]["participants"])
    
    # Assert
    assert count_after_removal == count_after_signup - 1
    assert email not in response_after.json()[activity]["participants"]


# ============================================================================
# Test: Edge cases
# ============================================================================
def test_signup_with_special_characters_in_email(client):
    """Test that signup works with valid email formats"""
    # Arrange
    email = "student+special@mergington.edu"
    activity = "Soccer Team"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
