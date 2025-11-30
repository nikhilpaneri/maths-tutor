import json
import os
from typing import Dict, Optional
from datetime import datetime
from models.student import StudentSession, StudentProgress
import asyncio


class MemoryService:
    """Service to manage student session memory and progress"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.sessions: Dict[str, StudentSession] = {}
        self._lock = asyncio.Lock()
        os.makedirs(data_dir, exist_ok=True)

    async def create_session(self, session_id: str, student_name: str, max_timestable: int) -> StudentSession:
        """Create a new student session"""
        async with self._lock:
            progress = StudentProgress(
                student_name=student_name,
                max_timestable=max_timestable
            )
            session = StudentSession(
                session_id=session_id,
                student_name=student_name,
                max_timestable=max_timestable,
                start_time=datetime.now(),
                progress=progress
            )
            self.sessions[session_id] = session
            await self._save_session(session)
            return session

    async def get_session(self, session_id: str) -> Optional[StudentSession]:
        """Get an existing session"""
        if session_id in self.sessions:
            return self.sessions[session_id]

        # Try loading from disk
        session = await self._load_session(session_id)
        if session:
            self.sessions[session_id] = session
        return session

    async def update_session(self, session: StudentSession):
        """Update session in memory and disk"""
        async with self._lock:
            self.sessions[session.session_id] = session
            await self._save_session(session)

    async def pause_session(self, session_id: str, state: Dict):
        """Pause a session and save its state"""
        session = await self.get_session(session_id)
        if session:
            session.is_paused = True
            session.current_state = state
            await self.update_session(session)

    async def resume_session(self, session_id: str) -> Optional[Dict]:
        """Resume a paused session"""
        session = await self.get_session(session_id)
        if session and session.is_paused:
            session.is_paused = False
            state = session.current_state
            session.current_state = None
            await self.update_session(session)
            return state
        return None

    async def _save_session(self, session: StudentSession):
        """Save session to disk"""
        file_path = os.path.join(self.data_dir, f"{session.session_id}.json")
        with open(file_path, 'w') as f:
            json.dump(session.model_dump(mode='json'), f, indent=2, default=str)

    async def _load_session(self, session_id: str) -> Optional[StudentSession]:
        """Load session from disk"""
        file_path = os.path.join(self.data_dir, f"{session_id}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as f:
            data = json.load(f)
            return StudentSession(**data)


# Global instance
memory_service = MemoryService()
