from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


class QuestionResult(BaseModel):
    timestable: int
    question: str
    answer: str
    correct: bool
    timestamp: datetime


class StudentProgress(BaseModel):
    student_name: str
    max_timestable: int
    total_questions: int = 0
    correct_answers: int = 0
    weak_areas: Dict[int, int] = {}  # timestable -> number of mistakes
    question_history: List[QuestionResult] = []

    def update_progress(self, timestable: int, correct: bool):
        """Update student progress after a question"""
        self.total_questions += 1
        if correct:
            self.correct_answers += 1
        else:
            if timestable not in self.weak_areas:
                self.weak_areas[timestable] = 0
            self.weak_areas[timestable] += 1

    def get_accuracy(self) -> float:
        """Calculate overall accuracy"""
        if self.total_questions == 0:
            return 0.0
        return (self.correct_answers / self.total_questions) * 100

    def get_weakest_timestables(self, limit: int = 3) -> List[int]:
        """Get the timestables the student struggles with most"""
        if not self.weak_areas:
            return []
        sorted_weak = sorted(self.weak_areas.items(), key=lambda x: x[1], reverse=True)
        return [timestable for timestable, _ in sorted_weak[:limit]]


class StudentSession(BaseModel):
    session_id: str
    student_name: str
    max_timestable: int
    start_time: datetime
    progress: StudentProgress
    is_paused: bool = False
    current_state: Optional[Dict] = None
