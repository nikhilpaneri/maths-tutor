import random
from typing import Dict, Any
from google import genai
import logging

logger = logging.getLogger(__name__)


class FactsAgent:
    """Agent responsible for sharing fun facts and educational quizzes"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-lite"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.agent_name = "FactsExpert"

        # Categories of facts suitable for kids
        self.fact_categories = [
            "animals",
            "space",
            "dinosaurs",
            "oceans",
            "nature",
            "inventions",
            "sports",
            "food",
            "countries"
        ]

    async def get_fun_fact(self) -> Dict[str, Any]:
        """Generate a fun fact for kids"""
        category = random.choice(self.fact_categories)

        logger.info(f"[{self.agent_name}] Generating fun fact about {category}")

        prompt = f"""Generate a fascinating, fun fact about {category} that would excite a child aged 5-10.

Requirements:
- Make it amazing and mind-blowing!
- Use simple, easy-to-understand language
- Keep it to 2-3 sentences
- Make it educational but fun
- Include a surprising detail or number if possible

Return ONLY the fact, nothing else."""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )

        fact = response.text.strip()

        logger.info(f"[{self.agent_name}] Generated fact: {fact[:50]}...")

        return {
            "type": "fact",
            "category": category,
            "content": fact
        }

    async def get_number_fact(self, number: int) -> Dict[str, Any]:
        """Generate a fun fact about a specific number"""
        logger.info(f"[{self.agent_name}] Generating number fact for {number}")

        prompt = f"""Generate a fun, interesting fact about the number {number} that would fascinate a child aged 5-10.

Ideas:
- Historical significance
- Appearances in nature
- Cool mathematical properties
- Sports connections
- Fun patterns

Requirements:
- Make it exciting and memorable!
- Use simple language
- 2-3 sentences max
- Make it educational but entertaining

Return ONLY the fact, nothing else."""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )

        fact = response.text.strip()

        logger.info(f"[{self.agent_name}] Generated number fact: {fact[:50]}...")

        return {
            "type": "number_fact",
            "number": number,
            "content": fact
        }

    async def generate_fact_quiz(self) -> Dict[str, Any]:
        """Generate a fun fact-based quiz question"""
        category = random.choice(self.fact_categories)

        logger.info(f"[{self.agent_name}] Generating fact quiz about {category}")

        prompt = f"""Create a fun, simple multiple-choice quiz question about {category} for kids aged 5-10.

Requirements:
- Make it interesting and educational
- Use simple language
- Provide 4 answer options (A, B, C, D)
- Make sure one answer is clearly correct
- Make the other options plausible but clearly wrong
- Keep the question short and clear

Format your response EXACTLY like this:
QUESTION: [the question]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
CORRECT: [A, B, C, or D]
EXPLANATION: [1 sentence why this is the answer]"""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )

        quiz_text = response.text.strip()

        # Parse the response
        try:
            lines = quiz_text.split('\n')
            question = ""
            options = {}
            correct_answer = ""
            explanation = ""

            for line in lines:
                line = line.strip()
                if line.startswith("QUESTION:"):
                    question = line.replace("QUESTION:", "").strip()
                elif line.startswith("A)"):
                    options["A"] = line.replace("A)", "").strip()
                elif line.startswith("B)"):
                    options["B"] = line.replace("B)", "").strip()
                elif line.startswith("C)"):
                    options["C"] = line.replace("C)", "").strip()
                elif line.startswith("D)"):
                    options["D"] = line.replace("D)", "").strip()
                elif line.startswith("CORRECT:"):
                    correct_answer = line.replace("CORRECT:", "").strip()
                elif line.startswith("EXPLANATION:"):
                    explanation = line.replace("EXPLANATION:", "").strip()

            logger.info(f"[{self.agent_name}] Generated quiz: {question[:50]}...")

            return {
                "type": "quiz",
                "category": category,
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": explanation
            }
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error parsing quiz: {e}")
            # Return a simple fallback
            return {
                "type": "quiz",
                "category": category,
                "question": quiz_text,
                "options": {},
                "correct_answer": "",
                "explanation": ""
            }

    async def evaluate_quiz_answer(self, quiz_data: Dict, user_answer: str) -> Dict[str, Any]:
        """Evaluate user's answer to a fact quiz"""
        user_answer = user_answer.strip().upper()
        correct_answer = quiz_data.get("correct_answer", "").strip().upper()

        is_correct = user_answer == correct_answer

        logger.info(f"[{self.agent_name}] Quiz answer evaluation: {is_correct}")

        # Generate feedback
        if is_correct:
            feedback_prompt = """Generate a SHORT enthusiastic response for a child (age 5-10) who got a quiz question correct!
Make it fun and encouraging. 1 sentence only."""
        else:
            feedback_prompt = f"""Generate a SHORT gentle response for a child (age 5-10) who got a quiz wrong.
Tell them the correct answer was {correct_answer} in a kind way. 1 sentence only."""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=feedback_prompt
        )

        feedback = response.text.strip()

        return {
            "correct": is_correct,
            "correct_answer": correct_answer,
            "explanation": quiz_data.get("explanation", ""),
            "feedback": feedback
        }

    async def pause_state(self) -> Dict[str, Any]:
        """Get current state for pausing"""
        return {
            "agent": self.agent_name,
            "status": "paused"
        }

    async def resume_from_state(self, state: Dict[str, Any]):
        """Resume from a paused state"""
        logger.info(f"[{self.agent_name}] Resuming from pause")
        return True
