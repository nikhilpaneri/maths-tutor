import os
import random
from typing import Dict, Any, Optional
from datetime import datetime
from google import genai
from google.genai import types
from services.memory_service import memory_service
from models.student import QuestionResult
import logging

logger = logging.getLogger(__name__)


class MathTutorAgent:
    """Agent responsible for teaching timestables with adaptive difficulty"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-lite"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.agent_name = "MathTutor"

    async def generate_question(self, session_id: str) -> Dict[str, Any]:
        """Generate a timestable question based on student's progress"""
        session = await memory_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        logger.info(f"[{self.agent_name}] Generating question for {session.student_name}")

        # Determine which timestable to ask about
        timestable = self._select_timestable(session)
        multiplier = random.randint(1, 12)

        # Generate creative question using LLM
        prompt = f"""You are a friendly math tutor for kids aged 5-10.
Generate a fun, engaging timestable question for {timestable} x {multiplier}.

Make it creative and age-appropriate. For example:
- "If you have {timestable} baskets with {multiplier} apples in each, how many apples do you have?"
- "A spider has 8 legs. If there are {multiplier} spiders, how many legs in total?"

Return ONLY the question text, make it fun and relatable for kids."""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )

        question_text = response.text.strip()

        logger.info(f"[{self.agent_name}] Generated question: {question_text}")

        return {
            "question": question_text,
            "timestable": timestable,
            "multiplier": multiplier,
            "expected_answer": timestable * multiplier,
            "session_id": session_id
        }

    async def evaluate_answer(self, session_id: str, question_data: Dict, user_answer: str) -> Dict[str, Any]:
        """Evaluate student's answer and provide feedback"""
        session = await memory_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            user_answer_num = int(user_answer)
            is_correct = user_answer_num == question_data["expected_answer"]
        except ValueError:
            is_correct = False
            user_answer_num = None

        logger.info(f"[{self.agent_name}] Answer evaluation: {is_correct}")

        # Update progress
        session.progress.update_progress(question_data["timestable"], is_correct)

        # Record in history
        result = QuestionResult(
            timestable=question_data["timestable"],
            question=question_data["question"],
            answer=user_answer,
            correct=is_correct,
            timestamp=datetime.now()
        )
        session.progress.question_history.append(result)

        await memory_service.update_session(session)

        # Generate encouraging feedback using LLM
        if is_correct:
            feedback_prompt = f"""Generate a SHORT, enthusiastic praise for a {session.student_name} (age 5-10) who correctly answered {question_data['expected_answer']}.
Make it encouraging and fun! Keep it to 1-2 short sentences. Use simple words."""
        else:
            feedback_prompt = f"""Generate a SHORT, gentle, encouraging message for a child (age 5-10) who got a math answer wrong.
The correct answer was {question_data['expected_answer']}.
Help them understand without making them feel bad. Keep it to 1-2 short sentences. Use simple words."""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=feedback_prompt
        )

        feedback = response.text.strip()

        return {
            "correct": is_correct,
            "expected_answer": question_data["expected_answer"],
            "feedback": feedback,
            "accuracy": session.progress.get_accuracy(),
            "total_questions": session.progress.total_questions
        }

    async def get_progress_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of student's progress"""
        session = await memory_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        weak_areas = session.progress.get_weakest_timestables()

        # Generate encouraging summary using LLM
        prompt = f"""You are a supportive math tutor. Generate a brief, encouraging progress summary for {session.student_name} (age 5-10).

Stats:
- Total questions: {session.progress.total_questions}
- Accuracy: {session.progress.get_accuracy():.1f}%
- Areas to practice: {weak_areas if weak_areas else 'None yet!'}

Keep it positive and motivating! Use simple words. 2-3 sentences max."""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )

        summary = response.text.strip()

        return {
            "student_name": session.student_name,
            "total_questions": session.progress.total_questions,
            "correct_answers": session.progress.correct_answers,
            "accuracy": session.progress.get_accuracy(),
            "weak_areas": weak_areas,
            "summary": summary
        }

    def _select_timestable(self, session) -> int:
        """Select which timestable to ask about based on student progress"""
        progress = session.progress

        # If student has weak areas, focus 70% of questions on those
        if progress.weak_areas and random.random() < 0.7:
            weak_timestables = progress.get_weakest_timestables()
            return random.choice(weak_timestables)

        # Otherwise, random timestable within their max level
        return random.randint(1, session.max_timestable)

    async def pause_state(self, session_id: str) -> Dict[str, Any]:
        """Get current state for pausing"""
        session = await memory_service.get_session(session_id)
        if not session:
            return {}

        return {
            "agent": self.agent_name,
            "progress": session.progress.model_dump(mode='json')
        }

    async def resume_from_state(self, session_id: str, state: Dict[str, Any]):
        """Resume from a paused state"""
        logger.info(f"[{self.agent_name}] Resuming session {session_id}")
        # State is already saved in memory service, just log the resume
        return True
