# RTI Voice Assistant - Local Setup Guide

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Step-by-Step Setup

### 1. Create Virtual Environment (Recommended)

**On Windows (PowerShell/CMD):**
```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# PowerShell:
venv\Scripts\Activate.ps1
# CMD:
venv\Scripts\activate.bat
```

**On Mac/Linux:**
```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (web server)
- Pydantic (data validation)
- Other required packages

### 3. Start the Server

```bash
uvicorn app:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

### 4. Test the API

**Option A: Run automated tests**

Open a new terminal (keep server running), activate venv, then:
```bash
python test_api.py
```

**Option B: Open browser**

Go to: http://localhost:8000/docs

You'll see interactive API documentation where you can test all endpoints!

**Option C: Use curl**

```bash
# Health check
curl http://localhost:8000/health

# Create session
curl -X POST http://localhost:8000/session/create \
  -H "Content-Type: application/json" \
  -d "{\"language\":\"hi\"}"
```

## Common Issues

### "python not found"
- Try `python3` instead of `python`
- Make sure Python is installed: `python --version`

### "pip not found"
- Try `python -m pip` instead of `pip`

### "Port 8000 already in use"
- Use a different port: `uvicorn app:app --reload --port 8001`

### "Module not found"
- Make sure venv is activated (you should see `(venv)` in prompt)
- Run `pip install -r requirements.txt` again

### Can't activate venv on Windows
- If PowerShell gives execution policy error:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## Deactivate Virtual Environment

When you're done:
```bash
deactivate
```

## Next Steps

Once the backend is running:
1. Test all endpoints at http://localhost:8000/docs
2. Build the frontend
3. Connect frontend to this API
4. Add real AWS services later (Polly, Bedrock, DynamoDB)

## Project Structure

```
backend/
├── app.py              # Main FastAPI application (ALL ENDPOINTS HERE)
├── requirements.txt    # Python dependencies
├── test_api.py        # Test suite
├── SETUP.md           # This file
├── README.md          # API documentation
└── shared/            # Shared utilities (config, models, AWS clients)
```

## Quick Reference

**Start server:**
```bash
uvicorn app:app --reload
```

**Run tests:**
```bash
python test_api.py
```

**View API docs:**
http://localhost:8000/docs

**Stop server:**
Press `Ctrl+C` in the terminal
