"""
Pytest configuration and shared fixtures for testing.
"""
import pytest
import os
import sys
from unittest.mock import Mock, AsyncMock
from datetime import datetime

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def mock_api_key():
    """Provide a mock API key for testing"""
    return "test_api_key_12345"


@pytest.fixture
def mock_model_name():
    """Provide a mock model name for testing"""
    return "gemini-2.5-flash-lite"


@pytest.fixture
def sample_session_data():
    """Provide sample session data for testing"""
    return {
        "session_id": "test-session-123",
        "student_name": "TestStudent",
        "max_timestable": 10,
        "start_time": datetime.now(),
    }


@pytest.fixture
def sample_question_data():
    """Provide sample question data for testing"""
    return {
        "question": "If you have 5 baskets with 6 apples in each, how many apples do you have?",
        "timestable": 5,
        "multiplier": 6,
        "expected_answer": 30,
        "session_id": "test-session-123"
    }


@pytest.fixture
def sample_quiz_data():
    """Provide sample quiz data for testing"""
    return {
        "type": "quiz",
        "category": "animals",
        "question": "How many legs does a spider have?",
        "options": {
            "A": "6 legs",
            "B": "8 legs",
            "C": "10 legs",
            "D": "4 legs"
        },
        "correct_answer": "B",
        "explanation": "Spiders are arachnids and have 8 legs!"
    }


@pytest.fixture
def mock_genai_client():
    """Mock Google GenAI client"""
    mock_client = Mock()
    mock_models = Mock()

    # Mock generate_content to return a response
    mock_response = Mock()
    mock_response.text = "This is a test response from the AI model."
    mock_models.generate_content = Mock(return_value=mock_response)

    mock_client.models = mock_models
    return mock_client


@pytest.fixture
async def clean_test_data():
    """Clean up test data directory after tests"""
    yield
    # Cleanup code can go here if needed
    import shutil
    test_data_dir = "tests/test_data"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
