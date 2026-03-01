# RTI Voice Assistant - Backend

Single FastAPI application for the RTI Voice Assistant prototype.

## Quick Start

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Start the server:**
```bash
uvicorn app:app --reload --port 8000
```

3. **Test the API:**
```bash
python test_api.py
```

Or open http://localhost:8000/docs for interactive API documentation.

## API Endpoints

### Voice Services
- `POST /voice/transcribe` - Convert speech to text
- `POST /voice/tts` - Convert text to speech

### Session Management
- `POST /session/create` - Create new session
- `GET /session/{id}` - Get session data
- `DELETE /session/{id}` - Delete session

### RTI Form
- `POST /form/{session_id}/update` - Update form field
- `GET /form/{session_id}` - Get form data
- `POST /form/{session_id}/generate` - Generate RTI document
- `GET /form/{session_id}/download` - Download document

### Legal Guidance
- `POST /guidance/explain` - Explain RTI rights
- `POST /guidance/next-steps` - Get next steps

## Development

### Run with auto-reload:
```bash
uvicorn app:app --reload --port 8000
```

### Run tests:
```bash
python test_api.py
```

### View API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

```
backend/
├── app.py              # Main FastAPI application
├── requirements.txt    # Python dependencies
├── test_api.py        # API test suite
├── shared/            # Shared utilities
│   ├── config.py      # Configuration
│   ├── models.py      # Data models
│   └── aws_clients.py # AWS SDK clients
└── README.md          # This file
```

## Current Status

**Working (Mock Data):**
- ✓ Voice transcription endpoint
- ✓ TTS endpoint
- ✓ Session management
- ✓ Form CRUD operations
- ✓ Document generation
- ✓ Legal guidance

**To Add:**
- [ ] Real IndicWhisper integration
- [ ] AWS Polly TTS
- [ ] Amazon Bedrock for legal simplification
- [ ] DynamoDB for sessions
- [ ] S3 for document storage
- [ ] PDF generation

## Deployment

### Local Development
```bash
uvicorn app:app --reload
```

### Production (AWS Lambda)
Will add deployment scripts once core features are tested locally.

## Testing with Frontend

The API has CORS enabled, so you can test with the frontend:

```javascript
// Create session
const session = await fetch('http://localhost:8000/session/create', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ language: 'hi' })
});

// Transcribe audio
const result = await fetch('http://localhost:8000/voice/transcribe', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    audio: audioBase64,
    language: 'hi'
  })
});
```

## Next Steps

1. Test all endpoints locally
2. Build frontend integration
3. Add real AWS services (Polly, Bedrock, DynamoDB)
4. Deploy to AWS Lambda
