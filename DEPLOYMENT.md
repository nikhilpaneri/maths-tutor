# Timestable Tutor - Deployment Instructions for macOS

This guide will help you deploy the Timestable Tutor application on your Mac.

## Prerequisites

Before you begin, make sure you have the following installed:

1. **Python 3.9+** - Check with `python3 --version`
2. **Node.js 18+** - Check with `node --version`
3. **npm** - Check with `npm --version`
4. **Google AI API Key** - Get one from [Google AI Studio](https://aistudio.google.com/apikey)

## Step 1: Set Up the Environment

### 1.1 Configure API Key

Edit the `.env` file in the project root and add your Google API key:

Replace the empty `GOOGLE_API_KEY=` with your actual API key:

```env
GOOGLE_API_KEY=your_actual_api_key_here
GOOGLE_MODEL=gemini-2.5-flash-lite
BACKEND_PORT=8000
```

Save and exit (Ctrl+O, Enter, Ctrl+X in nano).

## Step 2: Set Up Python Backend

### 2.1 Navigate to Backend Directory

```bash
cd backend
```

### 2.2 Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 2.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- google-genai (Google AI SDK)
- google-adk (Google Agent Development Kit)
- fastapi (Web framework)
- uvicorn (ASGI server)
- pydantic (Data validation)
- python-dotenv (Environment variables)
- httpx (HTTP client)
- aiofiles (Async file operations)

### 2.4 Create Data Directory

```bash
mkdir -p data
```

This directory will store:
- Student session data
- Progress tracking
- Logs
- Metrics and traces

## Step 3: Set Up Next.js Frontend

### 3.1 Navigate to Project Root

```bash
cd ..
```

### 3.2 Install Node Dependencies

```bash
npm install
```

This will install all required Next.js dependencies.

## Step 4: Run the Application

You'll need **two terminal windows** to run both the backend and frontend.

### Terminal 1: Start Python Backend

```bash
# Navigate to project root

# Activate virtual environment
source backend/venv/bin/activate

# Start the backend server
cd backend
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The backend API will be available at: **http://localhost:8000**

### Terminal 2: Start Next.js Frontend

```bash
# Navigate to project root

# Start the development server
npm run dev
```

You should see:
```
▲ Next.js 16.0.5
- Local:        http://localhost:3000
```

The web app will be available at: **http://localhost:3000**

## Step 5: Access the Application

1. Open your web browser
2. Navigate to **http://localhost:3000**
3. You should see the Timestable Tutor welcome screen!

## Using the Application

### Starting a Session

1. Enter the student's name
2. Select the maximum timestable level (1-12)
3. Click "Let's Start Learning!"

### During a Session

- **Math Questions**: Answer timestable questions with adaptive difficulty
- **Fun Facts**: Enjoy educational facts between questions
- **Quizzes**: Test your general knowledge with fun quizzes
- **View Progress**: Click to see accuracy and weak areas
- **Pause**: Pause the session and resume later
- **End Session**: End the session and see final progress

### Features

- **Adaptive Learning**: The system tracks which timestables you struggle with and focuses on those
- **Parallel Agents**: Math Tutor and Facts agents run concurrently
- **Pause/Resume**: Sessions can be paused and resumed without losing progress
- **Progress Tracking**: All answers are saved with timestamps
- **Encouraging Feedback**: AI-generated positive feedback for kids

## Observability Features

### View Metrics

Access system metrics at: **http://localhost:8000/api/metrics**

This shows:
- Request counts
- Latencies
- Error rates
- Agent call statistics

### View Traces

Access trace logs at: **http://localhost:8000/api/traces**

This shows:
- All API calls
- Agent interactions
- Timestamps
- Request flow

### View Logs

Backend logs are saved to: `backend/data/app.log`

```bash
tail -f backend/data/app.log
```

### Session Data

Student sessions are saved to: `backend/data/<session_id>.json`

```bash
ls -la backend/data/
```

## Troubleshooting

### Backend Won't Start

**Error: "GOOGLE_API_KEY not found"**
- Make sure you've set the API key in `.env`
- Check that `.env` is in the project root directory

**Error: "ModuleNotFoundError"**
- Make sure you activated the virtual environment: `source backend/venv/bin/activate`
- Reinstall dependencies: `pip install -r backend/requirements.txt`

**Error: "Address already in use"**
- Port 8000 is already taken
- Change `BACKEND_PORT` in `.env` to another port (e.g., 8001)
- Update `.env.local` to match: `NEXT_PUBLIC_API_URL=http://localhost:8001`

### Frontend Won't Start

**Error: "EADDRINUSE"**
- Port 3000 is already taken
- Run on a different port: `npm run dev -- -p 3001`
- Update `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000` (backend URL stays the same)

**Error: "Cannot connect to backend"**
- Make sure the backend is running on port 8000
- Check the backend URL in `.env.local`
- Check CORS settings in `backend/main.py`

### API Errors

**Error: "Rate limit exceeded"**
- You've hit Google AI's rate limit
- Wait a few minutes before trying again
- Consider upgrading your API plan

**Error: "Invalid API key"**
- Check that your API key is correct in `.env`
- Get a new key from [Google AI Studio](https://aistudio.google.com/apikey)

## Architecture Overview

### Agents (A2A Protocol)

1. **Coordinator Agent**
   - Orchestrates the learning experience
   - Decides when to show math questions vs fun content
   - Manages session lifecycle
   - Coordinates between Math Tutor and Facts agents

2. **Math Tutor Agent**
   - Generates timestable questions
   - Evaluates answers
   - Tracks student progress
   - Adapts difficulty based on weak areas
   - Uses memory service for persistence

3. **Facts Agent**
   - Generates fun facts from various categories
   - Creates number-specific facts
   - Generates and evaluates quiz questions
   - Keeps kids engaged between math questions

### Communication Flow

```
Frontend (Next.js)
    ↓ HTTP/JSON
Backend API (FastAPI)
    ↓ A2A Protocol
Coordinator Agent
    ↓ Parallel Execution
┌───────────────┬───────────────┐
Math Tutor      Facts Agent
    ↓                 ↓
Memory Service   Google AI
```

### Data Storage

- **Session Data**: JSON files in `backend/data/`
- **Logs**: Text logs in `backend/data/app.log`
- **Metrics**: In-memory, exportable to JSON
- **Traces**: In-memory, exportable to JSON

## Next Steps: Google Cloud Deployment (Future)

This application is designed to be cloud-ready. Future deployment will use:

- **Cloud Run**: For containerized backend
- **App Engine** or **Vercel**: For Next.js frontend
- **Cloud Firestore**: For session persistence
- **Cloud Logging**: For centralized logs
- **Cloud Monitoring**: For metrics and traces
- **Secret Manager**: For API keys

## Development Tips

### Running Tests

The project includes comprehensive tests with 93%+ coverage.

**Quick test run:**
```bash
# Run all tests with coverage
./run-tests.sh
```

**Manual test run:**
```bash
# Run all tests
cd backend
source venv/bin/activate
pytest

# Run specific test file
pytest tests/test_math_tutor_agent.py

# Run with coverage report
pytest --cov --cov-report=html

# View coverage report
open backend/htmlcov/index.html
```

**Test categories:**
- Unit tests for agents, services, models
- Integration tests for API endpoints
- Async tests for concurrent operations
- 45+ test cases covering all major functionality

See [TESTING.md](../TESTING.md) for detailed testing documentation.

### Hot Reload

Both backend and frontend support hot reload:
- Backend: Changes to Python files will auto-reload
- Frontend: Changes to React components will auto-reload

### Adding New Agents

1. Create new agent file in `backend/agents/`
2. Implement required methods (similar to existing agents)
3. Register in `coordinator_agent.py`
4. Add new API endpoints in `main.py`

### Modifying the Model

To use a different Google AI model, edit `.env`:

```env
# Use the faster flash-lite model (cheaper)
GOOGLE_MODEL=gemini-2.5-flash-lite

# Or use the standard flash model
GOOGLE_MODEL=gemini-2.5-flash

# Or use other available models
GOOGLE_MODEL=gemini-1.5-pro
```

## Support

For issues or questions:
1. Check the logs: `backend/data/app.log`
2. Check browser console for frontend errors
3. Review the metrics endpoint for system health
4. Check session data files for corruption

## License

This is an educational project for teaching timestables to primary school children.

---

**Enjoy learning with Timestable Tutor!**
