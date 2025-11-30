# Quick Start Guide

Get the Timestable Tutor running in just a few steps!

## Prerequisites Check

Before starting, make sure you have:

1. **Python 3.9+**
   ```bash
   python3 --version
   ```

2. **Node.js 18+**
   ```bash
   node --version
   ```

3. **Add your Google API Key** in `.env` ([Get one here](https://aistudio.google.com/apikey))

   Edit the `.env` file:
   ```bash
   GOOGLE_API_KEY=your_api_key_here
   GOOGLE_MODEL=gemini-2.5-flash-lite
   BACKEND_PORT=8000
   ```

## Option 1: Using the Startup Scripts (Easiest)

### Step 1: Start the Backend

Open a terminal and run:

```bash
./start-backend.sh
```

You should see:
```
Starting Timestable Tutor Backend...
Backend server starting on port 8000
```

**Keep this terminal open!**

### Step 2: Start the Frontend

Open a **second terminal** and run:

```bash
./start-frontend.sh
```

You should see:
```
Starting Timestable Tutor Frontend...
Frontend starting on port 3000
```

### Step 3: Open in Browser

Go to: **http://localhost:3000**

## Option 2: Manual Start

If the scripts don't work, start manually:

### Terminal 1 - Backend:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Terminal 2 - Frontend:

```bash
npm install
npm run dev
```

## Testing the Application

1. **Enter a name**: e.g., "Alex"
2. **Select level**: e.g., "10 times table"
3. **Click "Let's Start Learning!"**

You should see:
- A welcome message
- Your first math question or fun fact

## Verify Everything Works

### Check Backend API

In a browser, visit: **http://localhost:8000**

You should see:
```json
{
  "status": "healthy",
  "service": "Timestable Tutor API",
  "version": "1.0.0"
}
```

### Check Metrics

Visit: **http://localhost:8000/api/metrics**

You should see metrics data in JSON format.

### Check Logs

In a terminal:
```bash
tail -f backend/data/app.log
```

You should see log entries as you interact with the app.

## Common Issues

### "GOOGLE_API_KEY not found"
- Check that `.env` file exists in the project root
- Verify your API key is set: `GOOGLE_API_KEY=your_key_here`

### "Port already in use"
- Something else is using port 8000 or 3000
- Close other apps or change ports in `.env`

### "Module not found"
- Backend: Make sure you activated the virtual environment
- Frontend: Run `npm install` again

### "Cannot connect to backend"
- Make sure the backend is running (check Terminal 1)
- Check the backend URL in `.env.local`

## Next Steps

Once everything is running:

1. **Try all features**:
   - Answer math questions
   - Read fun facts
   - Take quizzes
   - View your progress
   - Pause and resume

2. **Monitor the system**:
   - Check metrics endpoint
   - Watch the logs
   - View traces

3. **Customize**:
   - Change the model in `.env`
   - Modify agent behavior in `backend/agents/`
   - Update UI in `app/components/`

## Need Help?

See the full documentation:
- [README.md](README.md) - Project overview
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide

## Stopping the Application

Press **Ctrl+C** in both terminal windows to stop the servers.

---

Enjoy learning timestables!
