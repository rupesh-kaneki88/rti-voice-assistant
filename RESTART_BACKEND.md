# How to Restart Backend with New Changes

## The Issue

The backend server was still running with old Bedrock code in memory. Changes to files don't take effect until you restart the server.

## Solution: Restart the Backend

### Step 1: Stop the Current Backend

In the terminal where backend is running, press:
```
Ctrl + C
```

You should see the server stop.

### Step 2: Restart the Backend

```bash
cd backend
python app.py
```

### Step 3: Verify New Code is Running

You should now see:
```
INFO:app:Initializing AWS services...
✓ Primary LLM: Groq (llama-3.1-70b-versatile)
✓ Fallback LLM: Gemini (gemini-1.5-flash)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**NOT** this (old):
```
INFO:app:Initializing AWS services...
INFO:app:✓ AWS services initialized
```

---

## What Was Fixed

### Removed from app.py:
- ❌ `from services.bedrock_service import BedrockService`
- ❌ `bedrock_service = None`
- ❌ `bedrock_service = BedrockService()`
- ❌ All Bedrock API calls

### Now Uses:
- ✅ `RTIAgentService` with Groq/Gemini
- ✅ No Bedrock dependencies
- ✅ Faster responses
- ✅ No payment issues

---

## Test the New System

### 1. Check Health Endpoint

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "services": {
    "rti_agent": true,
    "polly": true,
    "transcribe": true
  }
}
```

**NOT** `"bedrock": true`

### 2. Test Conversation

```bash
curl -X POST http://localhost:8000/session/create \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'
```

Copy the `session_id` from response, then:

```bash
curl -X POST http://localhost:8000/session/YOUR_SESSION_ID/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "I want education info", "language": "en"}'
```

You should see:
```
Generating with Groq (llama-3.1-70b-versatile) for language=en
✓ Groq response: ...
```

---

## Common Issues

### "Module 'groq' not found"

Install dependencies:
```bash
cd backend
pip install groq google-generativeai
```

### "Groq client not initialized"

Add API keys to `.env`:
```bash
GROQ_API_KEY=gsk_your_key_here
GEMINI_API_KEY=AIza_your_key_here
```

### Still seeing Bedrock errors

1. Make sure you stopped the old server (Ctrl+C)
2. Check no other Python process is running on port 8000:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Mac/Linux
   lsof -i :8000
   ```
3. Kill any old processes
4. Restart: `python app.py`

### Port 8000 already in use

```bash
# Use different port
python app.py --port 8001

# Or kill the process using port 8000
# Windows: taskkill /PID <pid> /F
# Mac/Linux: kill -9 <pid>
```

---

## Verify Everything Works

### Checklist:

- [ ] Backend starts without errors
- [ ] See "Primary LLM: Groq" in logs
- [ ] See "Fallback LLM: Gemini" in logs
- [ ] No Bedrock errors in logs
- [ ] Health endpoint shows `rti_agent: true`
- [ ] Conversation endpoint works
- [ ] Frontend can connect and chat

---

## Frontend Doesn't Need Restart

The frontend doesn't need to be restarted - it just calls the backend API. Once backend is restarted with new code, frontend will automatically use the new system.

---

## Quick Restart Script

Save this as `restart.sh` (Mac/Linux) or `restart.bat` (Windows):

**Mac/Linux** (`restart.sh`):
```bash
#!/bin/bash
cd backend
echo "Stopping any running backend..."
pkill -f "python app.py"
sleep 2
echo "Starting backend with new code..."
python app.py
```

**Windows** (`restart.bat`):
```batch
@echo off
cd backend
echo Stopping any running backend...
taskkill /F /IM python.exe
timeout /t 2
echo Starting backend with new code...
python app.py
```

Then just run:
```bash
./restart.sh  # Mac/Linux
restart.bat   # Windows
```

---

## Success!

Once you see:
```
✓ Primary LLM: Groq (llama-3.1-70b-versatile)
✓ Fallback LLM: Gemini (gemini-1.5-flash)
```

You're running the new code! 🎉

No more Bedrock, no more payment issues, much faster responses!
