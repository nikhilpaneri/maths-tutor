import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from agents.coordinator_agent import CoordinatorAgent
from utils.logging_config import metrics_collector, trace_logger, setup_logging
import logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(log_level="INFO", log_file="data/app.log")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Timestable Tutor API", version="1.0.0")

# CORS middleware for Next.js frontend - allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=False,  # Must be False when allow_origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize coordinator agent
api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash-lite")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

coordinator = CoordinatorAgent(api_key=api_key, model_name=model_name)

logger.info(f"Starting Timestable Tutor API with model: {model_name}")


# Request/Response Models
class StartSessionRequest(BaseModel):
    student_name: str
    max_timestable: int


class AnswerRequest(BaseModel):
    session_id: str
    answer: str
    question_data: Dict[str, Any]


class QuizAnswerRequest(BaseModel):
    answer: str
    quiz_data: Dict[str, Any]


class SessionRequest(BaseModel):
    session_id: str


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    metrics_collector.record_request("root")
    return {
        "status": "healthy",
        "service": "Timestable Tutor API",
        "version": "1.0.0"
    }


@app.post("/api/session/start")
async def start_session(request: StartSessionRequest):
    """Start a new learning session"""
    try:
        metrics_collector.record_request("start_session")
        session_id = str(uuid.uuid4())

        trace_id = str(uuid.uuid4())
        trace_logger.trace(
            trace_id,
            "API",
            "start_session",
            {"student_name": request.student_name, "max_timestable": request.max_timestable}
        )

        result = await coordinator.start_session(
            session_id,
            request.student_name,
            request.max_timestable
        )

        trace_logger.trace(trace_id, "Coordinator", "session_started", {"session_id": session_id})

        return {
            "success": True,
            "session_id": session_id,
            **result
        }
    except Exception as e:
        logger.error(f"Error starting session: {e}", exc_info=True)
        metrics_collector.record_error("start_session_error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/activity/next")
async def get_next_activity(request: SessionRequest):
    """Get the next activity (question, fact, or quiz)"""
    try:
        metrics_collector.record_request("next_activity")

        trace_id = str(uuid.uuid4())
        trace_logger.trace(trace_id, "API", "get_next_activity", {"session_id": request.session_id})

        result = await coordinator.get_next_activity(request.session_id)

        trace_logger.trace(
            trace_id,
            "Coordinator",
            "activity_generated",
            {"type": result.get("type", "unknown")}
        )

        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error getting next activity: {e}", exc_info=True)
        metrics_collector.record_error("next_activity_error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/answer/math")
async def submit_math_answer(request: AnswerRequest):
    """Submit an answer to a math question"""
    try:
        metrics_collector.record_request("submit_math_answer")

        trace_id = str(uuid.uuid4())
        trace_logger.trace(
            trace_id,
            "API",
            "submit_math_answer",
            {"session_id": request.session_id, "answer": request.answer}
        )

        result = await coordinator.process_math_answer(
            request.session_id,
            request.question_data,
            request.answer
        )

        trace_logger.trace(
            trace_id,
            "MathTutor",
            "answer_evaluated",
            {"correct": result["correct"]}
        )

        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error submitting math answer: {e}", exc_info=True)
        metrics_collector.record_error("submit_math_answer_error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/answer/quiz")
async def submit_quiz_answer(request: QuizAnswerRequest):
    """Submit an answer to a fact quiz"""
    try:
        metrics_collector.record_request("submit_quiz_answer")

        trace_id = str(uuid.uuid4())
        trace_logger.trace(trace_id, "API", "submit_quiz_answer", {"answer": request.answer})

        result = await coordinator.process_quiz_answer(
            request.quiz_data,
            request.answer
        )

        trace_logger.trace(
            trace_id,
            "FactsAgent",
            "quiz_evaluated",
            {"correct": result["correct"]}
        )

        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error submitting quiz answer: {e}", exc_info=True)
        metrics_collector.record_error("submit_quiz_answer_error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/session/progress")
async def get_progress(request: SessionRequest):
    """Get student progress"""
    try:
        metrics_collector.record_request("get_progress")

        trace_id = str(uuid.uuid4())
        trace_logger.trace(trace_id, "API", "get_progress", {"session_id": request.session_id})

        result = await coordinator.get_progress(request.session_id)

        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error getting progress: {e}", exc_info=True)
        metrics_collector.record_error("get_progress_error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/session/pause")
async def pause_session(request: SessionRequest):
    """Pause a session"""
    try:
        metrics_collector.record_request("pause_session")

        trace_id = str(uuid.uuid4())
        trace_logger.trace(trace_id, "API", "pause_session", {"session_id": request.session_id})

        result = await coordinator.pause_session(request.session_id)

        trace_logger.trace(trace_id, "Coordinator", "session_paused", {})

        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error pausing session: {e}", exc_info=True)
        metrics_collector.record_error("pause_session_error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/session/resume")
async def resume_session(request: SessionRequest):
    """Resume a paused session"""
    try:
        metrics_collector.record_request("resume_session")

        trace_id = str(uuid.uuid4())
        trace_logger.trace(trace_id, "API", "resume_session", {"session_id": request.session_id})

        result = await coordinator.resume_session(request.session_id)

        trace_logger.trace(trace_id, "Coordinator", "session_resumed", {})

        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error resuming session: {e}", exc_info=True)
        metrics_collector.record_error("resume_session_error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/session/end")
async def end_session(request: SessionRequest):
    """End a session"""
    try:
        metrics_collector.record_request("end_session")

        trace_id = str(uuid.uuid4())
        trace_logger.trace(trace_id, "API", "end_session", {"session_id": request.session_id})

        result = await coordinator.end_session(request.session_id)

        trace_logger.trace(trace_id, "Coordinator", "session_ended", {})

        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error ending session: {e}", exc_info=True)
        metrics_collector.record_error("end_session_error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics"""
    try:
        return metrics_collector.get_metrics()
    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/traces")
async def get_traces(trace_id: Optional[str] = None):
    """Get trace logs"""
    try:
        return {
            "traces": trace_logger.get_traces(trace_id)
        }
    except Exception as e:
        logger.error(f"Error getting traces: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
