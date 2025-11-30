import random
import asyncio
from typing import Dict, Any, Optional
from google import genai
from agents.math_tutor_agent import MathTutorAgent
from agents.facts_agent import FactsAgent
from services.memory_service import memory_service
import logging

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """Coordinator agent that orchestrates the learning experience"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-lite"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.agent_name = "Coordinator"

        # Initialize child agents
        self.math_tutor = MathTutorAgent(api_key, model_name)
        self.facts_agent = FactsAgent(api_key, model_name)

        # Track what type of content to show next
        self.question_count = {}

    async def start_session(self, session_id: str, student_name: str, max_timestable: int) -> Dict[str, Any]:
        """Start a new learning session"""
        logger.info(f"[{self.agent_name}] Starting session for {student_name}")

        # Create session in memory
        await memory_service.create_session(session_id, student_name, max_timestable)

        # Generate welcome message
        prompt = f"""Generate a warm, enthusiastic welcome message for {student_name}, a child aged 5-10 who is starting to learn their timestables up to {max_timestable}.

Make it:
- Exciting and encouraging
- Friendly and fun
- Short (2-3 sentences)
- Mention that we'll learn math AND fun facts together!

Return ONLY the welcome message."""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )

        welcome_message = response.text.strip()

        self.question_count[session_id] = 0

        return {
            "type": "welcome",
            "message": welcome_message,
            "session_id": session_id
        }

    async def get_next_activity(self, session_id: str) -> Dict[str, Any]:
        """
        Coordinate between math questions and fun content.
        Uses A2A pattern to communicate between agents.
        """
        if session_id not in self.question_count:
            self.question_count[session_id] = 0

        self.question_count[session_id] += 1
        count = self.question_count[session_id]

        logger.info(f"[{self.agent_name}] Getting next activity (count: {count})")

        # Strategy: Every 3 math questions, insert a fun fact or quiz
        # Run agents in parallel where possible
        if count % 3 == 0:
            # Time for a fun break!
            # Randomly choose between fact and quiz
            if random.random() < 0.5:
                logger.info(f"[{self.agent_name}] -> Delegating to FactsAgent for fun fact")
                return await self.facts_agent.get_fun_fact()
            else:
                logger.info(f"[{self.agent_name}] -> Delegating to FactsAgent for quiz")
                return await self.facts_agent.generate_fact_quiz()
        else:
            # Math question time
            logger.info(f"[{self.agent_name}] -> Delegating to MathTutor for question")
            return await self.math_tutor.generate_question(session_id)

    async def process_math_answer(self, session_id: str, question_data: Dict, user_answer: str) -> Dict[str, Any]:
        """Process a math answer through the math tutor agent"""
        logger.info(f"[{self.agent_name}] -> Delegating answer evaluation to MathTutor")

        # Evaluate with math tutor
        result = await self.math_tutor.evaluate_answer(session_id, question_data, user_answer)

        # Occasionally add a number fact about the answer
        if result["correct"] and random.random() < 0.3:
            logger.info(f"[{self.agent_name}] -> Requesting bonus number fact from FactsAgent")
            number_fact = await self.facts_agent.get_number_fact(question_data["expected_answer"])
            result["bonus_fact"] = number_fact["content"]

        return result

    async def process_quiz_answer(self, quiz_data: Dict, user_answer: str) -> Dict[str, Any]:
        """Process a quiz answer through the facts agent"""
        logger.info(f"[{self.agent_name}] -> Delegating quiz evaluation to FactsAgent")
        return await self.facts_agent.evaluate_quiz_answer(quiz_data, user_answer)

    async def get_progress(self, session_id: str) -> Dict[str, Any]:
        """Get student progress summary"""
        logger.info(f"[{self.agent_name}] -> Requesting progress from MathTutor")
        return await self.math_tutor.get_progress_summary(session_id)

    async def pause_session(self, session_id: str) -> Dict[str, Any]:
        """Pause the session and save all agent states"""
        logger.info(f"[{self.agent_name}] Pausing session {session_id}")

        # Gather states from all agents in parallel
        math_state_task = asyncio.create_task(self.math_tutor.pause_state(session_id))
        facts_state_task = asyncio.create_task(self.facts_agent.pause_state())

        math_state, facts_state = await asyncio.gather(math_state_task, facts_state_task)

        state = {
            "coordinator": {
                "question_count": self.question_count.get(session_id, 0)
            },
            "math_tutor": math_state,
            "facts_agent": facts_state
        }

        await memory_service.pause_session(session_id, state)

        return {
            "status": "paused",
            "message": "Session paused successfully! You can resume anytime."
        }

    async def resume_session(self, session_id: str) -> Dict[str, Any]:
        """Resume a paused session"""
        logger.info(f"[{self.agent_name}] Resuming session {session_id}")

        state = await memory_service.resume_session(session_id)

        if state:
            # Restore coordinator state
            if "coordinator" in state:
                self.question_count[session_id] = state["coordinator"].get("question_count", 0)

            # Resume child agents in parallel
            math_resume_task = asyncio.create_task(
                self.math_tutor.resume_from_state(session_id, state.get("math_tutor", {}))
            )
            facts_resume_task = asyncio.create_task(
                self.facts_agent.resume_from_state(state.get("facts_agent", {}))
            )

            await asyncio.gather(math_resume_task, facts_resume_task)

            session = await memory_service.get_session(session_id)

            return {
                "status": "resumed",
                "message": f"Welcome back, {session.student_name}! Let's continue learning!",
                "session": session.model_dump(mode='json')
            }
        else:
            return {
                "status": "error",
                "message": "Could not find paused session"
            }

    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End the session with a summary"""
        logger.info(f"[{self.agent_name}] Ending session {session_id}")

        # Get final progress
        progress = await self.get_progress(session_id)

        # Generate farewell message
        prompt = f"""Generate a warm, encouraging goodbye message for a child (age 5-10) who just finished a timestables practice session.

Their stats:
- Questions answered: {progress['total_questions']}
- Accuracy: {progress['accuracy']:.1f}%

Make it:
- Congratulatory and proud
- Encouraging them to come back
- Short (2-3 sentences)
- Positive regardless of the score

Return ONLY the goodbye message."""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )

        farewell = response.text.strip()

        return {
            "type": "goodbye",
            "message": farewell,
            "progress": progress
        }
