"""
Tests for Facts Agent.

This module tests the fun facts generation, quiz creation,
and quiz evaluation functionality of the Facts Agent.
"""
import pytest
from unittest.mock import Mock, patch
from agents.facts_agent import FactsAgent


class TestFactsAgent:
    """Test suite for Facts Agent"""

    @pytest.fixture
    def agent(self, mock_api_key, mock_model_name):
        """Create a Facts Agent instance for testing"""
        with patch('agents.facts_agent.genai.Client') as mock_client:
            mock_client.return_value = Mock()
            agent = FactsAgent(mock_api_key, mock_model_name)
            return agent

    @pytest.mark.asyncio
    async def test_get_fun_fact(self, agent):
        """Test fun fact generation"""
        # Mock AI response
        mock_response = Mock()
        mock_response.text = "Did you know that octopuses have three hearts? Two pump blood to the gills, and one pumps it to the rest of the body!"
        agent.client.models.generate_content = Mock(return_value=mock_response)

        result = await agent.get_fun_fact()

        # Assertions
        assert result["type"] == "fact"
        assert "category" in result
        assert result["category"] in agent.fact_categories
        assert "content" in result
        assert len(result["content"]) > 0

    @pytest.mark.asyncio
    async def test_get_number_fact(self, agent):
        """Test number-specific fact generation"""
        test_number = 42

        # Mock AI response
        mock_response = Mock()
        mock_response.text = "The number 42 is special! It's the answer to the ultimate question of life in 'The Hitchhiker's Guide to the Galaxy'!"
        agent.client.models.generate_content = Mock(return_value=mock_response)

        result = await agent.get_number_fact(test_number)

        # Assertions
        assert result["type"] == "number_fact"
        assert result["number"] == test_number
        assert "content" in result
        assert len(result["content"]) > 0

    @pytest.mark.asyncio
    async def test_generate_fact_quiz(self, agent):
        """Test quiz generation"""
        # Mock AI response with properly formatted quiz
        mock_response = Mock()
        mock_response.text = """QUESTION: What is the largest planet in our solar system?
A) Earth
B) Jupiter
C) Saturn
D) Mars
CORRECT: B
EXPLANATION: Jupiter is the largest planet in our solar system!"""
        agent.client.models.generate_content = Mock(return_value=mock_response)

        result = await agent.generate_fact_quiz()

        # Assertions
        assert result["type"] == "quiz"
        assert "category" in result
        assert result["category"] in agent.fact_categories
        assert "question" in result
        assert "options" in result
        assert len(result["options"]) == 4  # Should have 4 options
        assert "A" in result["options"]
        assert "B" in result["options"]
        assert "C" in result["options"]
        assert "D" in result["options"]
        assert "correct_answer" in result
        assert result["correct_answer"] in ["A", "B", "C", "D"]
        assert "explanation" in result

    @pytest.mark.asyncio
    async def test_evaluate_quiz_answer_correct(self, agent, sample_quiz_data):
        """Test quiz answer evaluation when answer is correct"""
        # Mock AI feedback response
        mock_response = Mock()
        mock_response.text = "Fantastic! You got it right!"
        agent.client.models.generate_content = Mock(return_value=mock_response)

        result = await agent.evaluate_quiz_answer(sample_quiz_data, "B")

        # Assertions
        assert result["correct"] is True
        assert result["correct_answer"] == "B"
        assert "feedback" in result
        assert "explanation" in result

    @pytest.mark.asyncio
    async def test_evaluate_quiz_answer_incorrect(self, agent, sample_quiz_data):
        """Test quiz answer evaluation when answer is incorrect"""
        # Mock AI feedback response
        mock_response = Mock()
        mock_response.text = "Good try! The correct answer is B."
        agent.client.models.generate_content = Mock(return_value=mock_response)

        result = await agent.evaluate_quiz_answer(sample_quiz_data, "A")

        # Assertions
        assert result["correct"] is False
        assert result["correct_answer"] == "B"
        assert "feedback" in result
        assert "explanation" in result

    @pytest.mark.asyncio
    async def test_pause_resume_state(self, agent):
        """Test pause and resume functionality"""
        # Test pause
        pause_state = await agent.pause_state()
        assert pause_state["agent"] == "FactsExpert"
        assert pause_state["status"] == "paused"

        # Test resume
        result = await agent.resume_from_state(pause_state)
        assert result is True

    def test_fact_categories(self, agent):
        """Test that agent has appropriate fact categories for kids"""
        expected_categories = [
            "animals", "space", "dinosaurs", "oceans",
            "nature", "inventions", "sports", "food", "countries"
        ]
        assert agent.fact_categories == expected_categories

    @pytest.mark.asyncio
    async def test_quiz_parsing_handles_malformed_response(self, agent):
        """Test that quiz generation handles malformed AI responses gracefully"""
        # Mock AI response with malformed format
        mock_response = Mock()
        mock_response.text = "This is not a properly formatted quiz at all!"
        agent.client.models.generate_content = Mock(return_value=mock_response)

        result = await agent.generate_fact_quiz()

        # Should still return a quiz structure, even if empty
        assert result["type"] == "quiz"
        assert "question" in result
        # When parsing fails, it should return the raw text as question
        assert "options" in result
