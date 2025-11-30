"""
Tests for Math Tutor Agent.

This module tests the adaptive question generation, answer evaluation,
and progress tracking functionality of the Math Tutor Agent.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from agents.math_tutor_agent import MathTutorAgent
from models.student import StudentSession, StudentProgress
from datetime import datetime


class TestMathTutorAgent:
    """Test suite for Math Tutor Agent"""

    @pytest.fixture
    def agent(self, mock_api_key, mock_model_name):
        """Create a Math Tutor Agent instance for testing"""
        with patch('agents.math_tutor_agent.genai.Client') as mock_client:
            mock_client.return_value = Mock()
            agent = MathTutorAgent(mock_api_key, mock_model_name)
            return agent

    @pytest.mark.asyncio
    async def test_generate_question_success(self, agent, sample_session_data):
        """Test that generate_question creates a valid timestable question"""
        # Mock memory service to return a test session
        progress = StudentProgress(
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"]
        )
        session = StudentSession(
            session_id=sample_session_data["session_id"],
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"],
            start_time=sample_session_data["start_time"],
            progress=progress
        )

        # Mock the AI response
        mock_response = Mock()
        mock_response.text = "If you have 3 baskets with 4 apples each, how many apples total?"
        agent.client.models.generate_content = Mock(return_value=mock_response)

        with patch('agents.math_tutor_agent.memory_service.get_session', return_value=session):
            result = await agent.generate_question(sample_session_data["session_id"])

        # Assertions
        assert "question" in result
        assert "timestable" in result
        assert "multiplier" in result
        assert "expected_answer" in result
        assert "session_id" in result
        assert result["session_id"] == sample_session_data["session_id"]
        assert 1 <= result["timestable"] <= sample_session_data["max_timestable"]
        assert 1 <= result["multiplier"] <= 12
        assert result["expected_answer"] == result["timestable"] * result["multiplier"]

    @pytest.mark.asyncio
    async def test_evaluate_answer_correct(self, agent, sample_session_data, sample_question_data):
        """Test answer evaluation when student provides correct answer"""
        # Setup test session
        progress = StudentProgress(
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"]
        )
        session = StudentSession(
            session_id=sample_session_data["session_id"],
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"],
            start_time=sample_session_data["start_time"],
            progress=progress
        )

        # Mock AI feedback response
        mock_response = Mock()
        mock_response.text = "Awesome job! You're a math superstar!"
        agent.client.models.generate_content = Mock(return_value=mock_response)

        with patch('agents.math_tutor_agent.memory_service.get_session', return_value=session):
            with patch('agents.math_tutor_agent.memory_service.update_session'):
                result = await agent.evaluate_answer(
                    sample_session_data["session_id"],
                    sample_question_data,
                    "30"  # Correct answer
                )

        # Assertions
        assert result["correct"] is True
        assert result["expected_answer"] == 30
        assert "feedback" in result
        assert result["total_questions"] == 1
        assert result["accuracy"] == 100.0

    @pytest.mark.asyncio
    async def test_evaluate_answer_incorrect(self, agent, sample_session_data, sample_question_data):
        """Test answer evaluation when student provides incorrect answer"""
        # Setup test session
        progress = StudentProgress(
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"]
        )
        session = StudentSession(
            session_id=sample_session_data["session_id"],
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"],
            start_time=sample_session_data["start_time"],
            progress=progress
        )

        # Mock AI feedback response
        mock_response = Mock()
        mock_response.text = "That's okay! Let's try again. The answer is 30!"
        agent.client.models.generate_content = Mock(return_value=mock_response)

        with patch('agents.math_tutor_agent.memory_service.get_session', return_value=session):
            with patch('agents.math_tutor_agent.memory_service.update_session'):
                result = await agent.evaluate_answer(
                    sample_session_data["session_id"],
                    sample_question_data,
                    "25"  # Incorrect answer
                )

        # Assertions
        assert result["correct"] is False
        assert result["expected_answer"] == 30
        assert "feedback" in result
        assert result["total_questions"] == 1
        assert result["accuracy"] == 0.0

    @pytest.mark.asyncio
    async def test_adaptive_question_selection(self, agent, sample_session_data):
        """Test that agent focuses on weak areas when generating questions"""
        # Create progress with weak areas
        progress = StudentProgress(
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"],
            total_questions=10,
            correct_answers=7,
            weak_areas={6: 3, 7: 2}  # Student struggles with 6 and 7 times tables
        )
        session = StudentSession(
            session_id=sample_session_data["session_id"],
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"],
            start_time=sample_session_data["start_time"],
            progress=progress
        )

        # Test _select_timestable method
        with patch('agents.math_tutor_agent.random.random', return_value=0.5):  # Will trigger weak area selection
            timestable = agent._select_timestable(session)
            assert timestable in [6, 7]  # Should select from weak areas

    @pytest.mark.asyncio
    async def test_get_progress_summary(self, agent, sample_session_data):
        """Test progress summary generation"""
        # Create progress with some history
        progress = StudentProgress(
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"],
            total_questions=20,
            correct_answers=16,
            weak_areas={8: 2, 9: 2}
        )
        session = StudentSession(
            session_id=sample_session_data["session_id"],
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"],
            start_time=sample_session_data["start_time"],
            progress=progress
        )

        # Mock AI summary response
        mock_response = Mock()
        mock_response.text = "Great progress! Keep practicing those 8s and 9s!"
        agent.client.models.generate_content = Mock(return_value=mock_response)

        with patch('agents.math_tutor_agent.memory_service.get_session', return_value=session):
            result = await agent.get_progress_summary(sample_session_data["session_id"])

        # Assertions
        assert result["student_name"] == sample_session_data["student_name"]
        assert result["total_questions"] == 20
        assert result["correct_answers"] == 16
        assert result["accuracy"] == 80.0
        assert 8 in result["weak_areas"]
        assert 9 in result["weak_areas"]
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_pause_resume_state(self, agent, sample_session_data):
        """Test pause and resume functionality"""
        # Create test session
        progress = StudentProgress(
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"]
        )
        session = StudentSession(
            session_id=sample_session_data["session_id"],
            student_name=sample_session_data["student_name"],
            max_timestable=sample_session_data["max_timestable"],
            start_time=sample_session_data["start_time"],
            progress=progress
        )

        with patch('agents.math_tutor_agent.memory_service.get_session', return_value=session):
            # Test pause
            pause_state = await agent.pause_state(sample_session_data["session_id"])
            assert pause_state["agent"] == "MathTutor"
            assert "progress" in pause_state

            # Test resume
            result = await agent.resume_from_state(sample_session_data["session_id"], pause_state)
            assert result is True
