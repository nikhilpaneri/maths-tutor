"""
Tests for API endpoints.

This module tests all REST API endpoints including session management,
activity generation, and answer submission.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from main import app


class TestAPI:
    """Test suite for API endpoints"""

    @pytest.fixture
    def client(self):
        """Create a test client for the API"""
        return TestClient(app)

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator agent"""
        with patch('main.coordinator') as mock:
            yield mock

    def test_root_endpoint(self, client):
        """Test the root health check endpoint"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Timestable Tutor API"
        assert "version" in data

    def test_start_session_success(self, client, mock_coordinator):
        """Test starting a new session successfully"""
        # Mock coordinator response
        mock_coordinator.start_session = AsyncMock(return_value={
            "type": "welcome",
            "message": "Welcome to Timestable Tutor!"
        })

        response = client.post("/api/session/start", json={
            "student_name": "Test Student",
            "max_timestable": 10
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "session_id" in data
        assert data["type"] == "welcome"
        assert "message" in data

    def test_start_session_missing_fields(self, client):
        """Test starting a session with missing required fields"""
        response = client.post("/api/session/start", json={
            "student_name": "Test Student"
            # missing max_timestable
        })

        assert response.status_code == 422  # Validation error

    def test_get_next_activity(self, client, mock_coordinator):
        """Test getting the next activity"""
        # Mock coordinator response
        mock_coordinator.get_next_activity = AsyncMock(return_value={
            "question": "What is 5 x 6?",
            "timestable": 5,
            "multiplier": 6,
            "expected_answer": 30
        })

        response = client.post("/api/activity/next", json={
            "session_id": "test-session-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "question" in data

    def test_submit_math_answer_correct(self, client, mock_coordinator):
        """Test submitting a correct math answer"""
        # Mock coordinator response
        mock_coordinator.process_math_answer = AsyncMock(return_value={
            "correct": True,
            "expected_answer": 30,
            "feedback": "Great job!",
            "accuracy": 100.0,
            "total_questions": 1
        })

        response = client.post("/api/answer/math", json={
            "session_id": "test-session-123",
            "answer": "30",
            "question_data": {
                "timestable": 5,
                "multiplier": 6,
                "expected_answer": 30
            }
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["correct"] is True
        assert "feedback" in data

    def test_submit_quiz_answer(self, client, mock_coordinator):
        """Test submitting a quiz answer"""
        # Mock coordinator response
        mock_coordinator.process_quiz_answer = AsyncMock(return_value={
            "correct": True,
            "correct_answer": "B",
            "explanation": "Correct!",
            "feedback": "Well done!"
        })

        response = client.post("/api/answer/quiz", json={
            "answer": "B",
            "quiz_data": {
                "question": "Test question?",
                "correct_answer": "B"
            }
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["correct"] is True

    def test_get_progress(self, client, mock_coordinator):
        """Test getting student progress"""
        # Mock coordinator response
        mock_coordinator.get_progress = AsyncMock(return_value={
            "student_name": "Test Student",
            "total_questions": 10,
            "correct_answers": 8,
            "accuracy": 80.0,
            "weak_areas": [7, 9],
            "summary": "Great progress!"
        })

        response = client.post("/api/session/progress", json={
            "session_id": "test-session-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_questions"] == 10
        assert data["accuracy"] == 80.0

    def test_pause_session(self, client, mock_coordinator):
        """Test pausing a session"""
        # Mock coordinator response
        mock_coordinator.pause_session = AsyncMock(return_value={
            "status": "paused",
            "message": "Session paused successfully!"
        })

        response = client.post("/api/session/pause", json={
            "session_id": "test-session-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["status"] == "paused"

    def test_resume_session(self, client, mock_coordinator):
        """Test resuming a paused session"""
        # Mock coordinator response
        mock_coordinator.resume_session = AsyncMock(return_value={
            "status": "resumed",
            "message": "Welcome back!"
        })

        response = client.post("/api/session/resume", json={
            "session_id": "test-session-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["status"] == "resumed"

    def test_end_session(self, client, mock_coordinator):
        """Test ending a session"""
        # Mock coordinator response
        mock_coordinator.end_session = AsyncMock(return_value={
            "type": "goodbye",
            "message": "Great work today!",
            "progress": {
                "total_questions": 15,
                "accuracy": 85.0
            }
        })

        response = client.post("/api/session/end", json={
            "session_id": "test-session-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["type"] == "goodbye"

    def test_get_metrics(self, client):
        """Test getting system metrics"""
        response = client.get("/api/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "uptime_seconds" in data
        assert "timestamp" in data
        assert "requests" in data

    def test_get_traces(self, client):
        """Test getting trace logs"""
        response = client.get("/api/traces")

        assert response.status_code == 200
        data = response.json()
        assert "traces" in data
        assert isinstance(data["traces"], list)

    def test_cors_headers(self, client):
        """Test that CORS headers are properly set"""
        response = client.options("/api/session/start", headers={
            "Origin": "http://localhost:3001",
            "Access-Control-Request-Method": "POST"
        })

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_error_handling(self, client, mock_coordinator):
        """Test that errors are handled gracefully"""
        # Mock coordinator to raise an exception
        mock_coordinator.start_session = AsyncMock(side_effect=Exception("Test error"))

        response = client.post("/api/session/start", json={
            "student_name": "Test Student",
            "max_timestable": 10
        })

        assert response.status_code == 500
