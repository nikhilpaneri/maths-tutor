"""
Tests for Memory Service.

This module tests session creation, retrieval, pause/resume,
and persistence functionality of the Memory Service.
"""
import pytest
import os
import tempfile
import shutil
from datetime import datetime
from services.memory_service import MemoryService
from models.student import StudentSession, StudentProgress


class TestMemoryService:
    """Test suite for Memory Service"""

    @pytest.fixture
    async def service(self):
        """Create a Memory Service with temporary data directory"""
        temp_dir = tempfile.mkdtemp()
        service = MemoryService(data_dir=temp_dir)
        yield service
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_create_session(self, service):
        """Test session creation"""
        session_id = "test-session-001"
        student_name = "Test Student"
        max_timestable = 10

        session = await service.create_session(session_id, student_name, max_timestable)

        # Assertions
        assert session.session_id == session_id
        assert session.student_name == student_name
        assert session.max_timestable == max_timestable
        assert session.progress.student_name == student_name
        assert session.progress.max_timestable == max_timestable
        assert session.progress.total_questions == 0
        assert session.progress.correct_answers == 0
        assert not session.is_paused

    @pytest.mark.asyncio
    async def test_get_session_from_memory(self, service):
        """Test retrieving a session from memory"""
        session_id = "test-session-002"
        student_name = "Memory Test"
        max_timestable = 12

        # Create session
        created_session = await service.create_session(session_id, student_name, max_timestable)

        # Retrieve session
        retrieved_session = await service.get_session(session_id)

        # Assertions
        assert retrieved_session is not None
        assert retrieved_session.session_id == created_session.session_id
        assert retrieved_session.student_name == created_session.student_name

    @pytest.mark.asyncio
    async def test_get_session_from_disk(self, service):
        """Test retrieving a session from disk after clearing memory"""
        session_id = "test-session-003"
        student_name = "Disk Test"
        max_timestable = 8

        # Create session
        await service.create_session(session_id, student_name, max_timestable)

        # Clear from memory
        service.sessions.clear()

        # Retrieve session (should load from disk)
        retrieved_session = await service.get_session(session_id)

        # Assertions
        assert retrieved_session is not None
        assert retrieved_session.session_id == session_id
        assert retrieved_session.student_name == student_name

    @pytest.mark.asyncio
    async def test_update_session(self, service):
        """Test updating a session"""
        session_id = "test-session-004"
        student_name = "Update Test"
        max_timestable = 10

        # Create session
        session = await service.create_session(session_id, student_name, max_timestable)

        # Modify session
        session.progress.total_questions = 5
        session.progress.correct_answers = 4

        # Update session
        await service.update_session(session)

        # Retrieve updated session
        updated_session = await service.get_session(session_id)

        # Assertions
        assert updated_session.progress.total_questions == 5
        assert updated_session.progress.correct_answers == 4

    @pytest.mark.asyncio
    async def test_pause_session(self, service):
        """Test pausing a session"""
        session_id = "test-session-005"
        student_name = "Pause Test"
        max_timestable = 10

        # Create session
        await service.create_session(session_id, student_name, max_timestable)

        # Pause session with state
        state = {"current_question": "What is 5 x 6?", "activity_count": 3}
        await service.pause_session(session_id, state)

        # Retrieve paused session
        paused_session = await service.get_session(session_id)

        # Assertions
        assert paused_session.is_paused is True
        assert paused_session.current_state == state

    @pytest.mark.asyncio
    async def test_resume_session(self, service):
        """Test resuming a paused session"""
        session_id = "test-session-006"
        student_name = "Resume Test"
        max_timestable = 10

        # Create and pause session
        await service.create_session(session_id, student_name, max_timestable)
        state = {"current_question": "What is 7 x 8?", "activity_count": 5}
        await service.pause_session(session_id, state)

        # Resume session
        resumed_state = await service.resume_session(session_id)

        # Retrieve session
        session = await service.get_session(session_id)

        # Assertions
        assert resumed_state == state
        assert session.is_paused is False
        assert session.current_state is None

    @pytest.mark.asyncio
    async def test_session_persistence(self, service):
        """Test that sessions are persisted to disk"""
        session_id = "test-session-007"
        student_name = "Persistence Test"
        max_timestable = 12

        # Create session
        await service.create_session(session_id, student_name, max_timestable)

        # Check that file exists on disk
        file_path = os.path.join(service.data_dir, f"{session_id}.json")
        assert os.path.exists(file_path)

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, service):
        """Test getting a session that doesn't exist"""
        session = await service.get_session("nonexistent-session")
        assert session is None

    @pytest.mark.asyncio
    async def test_concurrent_session_updates(self, service):
        """Test that concurrent updates use locking correctly"""
        import asyncio

        session_id = "test-session-008"
        student_name = "Concurrency Test"
        max_timestable = 10

        # Create session
        session = await service.create_session(session_id, student_name, max_timestable)

        # Simulate concurrent updates
        async def update_questions():
            session.progress.total_questions += 1
            await service.update_session(session)

        # Run multiple updates concurrently
        await asyncio.gather(*[update_questions() for _ in range(10)])

        # Retrieve final session
        final_session = await service.get_session(session_id)

        # Assertions - all updates should be reflected
        assert final_session.progress.total_questions == 10
