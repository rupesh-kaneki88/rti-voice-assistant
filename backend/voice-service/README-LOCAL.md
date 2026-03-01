# Local Testing Guide

This guide shows you how to test the Voice Service locally without Docker or AWS deployment.

## Setup

1. Install dependencies:
```bash
pip install -r requirements-local.txt
```

## Running the Server

Start the local FastAPI server:

```bash
uvicorn app_local:app --reload --port 8000
```

The server will start at `http://localhost:8000`

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Testing

### Option 1: Run Automated Tests

In a new terminal (keep the server running):

```bash
python test_local.py
```

This will run all tests and show results.

### Option 2: Manual Testing with curl

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Transcribe English:**
```bash
curl -X POST http://localhost:8000/voice/transcribe \
  -H "Content-Type: application/json" \
  -d "{\"audio\":\"dGVzdCBhdWRpbyBkYXRh\",\"language\":\"en\"}"
```

**Transcribe Hindi:**
```bash
curl -X POST http://localhost:8000/voice/transcribe \
  -H "Content-Type: application/json" \
  -d "{\"audio\":\"dGVzdCBhdWRpbyBkYXRh\",\"language\":\"hi\"}"
```

**Transcribe Kannada:**
```bash
curl -X POST http://localhost:8000/voice/transcribe \
  -H "Content-Type: application/json" \
  -d "{\"audio\":\"dGVzdCBhdWRpbyBkYXRh\",\"language\":\"kn\"}"
```

### Option 3: Interactive API Documentation

Open your browser and go to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

You can test all endpoints interactively from the browser!

## Testing with Real Audio

To test with a real audio file:

```python
import base64
import requests

# Read audio file
with open('sample.wav', 'rb') as f:
    audio_bytes = f.read()

# Encode to base64
audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

# Send request
response = requests.post(
    'http://localhost:8000/voice/transcribe',
    json={
        'audio': audio_base64,
        'language': 'hi'
    }
)

print(response.json())
```

## Expected Response

```json
{
  "text": "यह स्थानीय परीक्षण के लिए हिंदी में एक नकली प्रतिलेखन है।",
  "confidence": 0.95,
  "language": "hi",
  "mode": "LOCAL_TESTING",
  "message": "This is a mock response for local testing. Real transcription will use IndicWhisper."
}
```

## Next Steps

Once local testing works:

1. Test frontend integration with this local API
2. Build other services (session management, form service, etc.)
3. Deploy to AWS Lambda when ready

## Troubleshooting

**Port already in use:**
```bash
# Use a different port
uvicorn app_local:app --reload --port 8001
```

**Module not found:**
```bash
# Make sure you're in the voice-service directory
cd backend/voice-service
pip install -r requirements-local.txt
```

**CORS errors from frontend:**
The server has CORS enabled for all origins, so frontend should work fine.
