# Testing the RTI Conversational Agent

## Quick Start

### 1. Start the Backend

```bash
cd backend
python app.py
```

You should see:
```
INFO:app:Initializing AWS services...
INFO:app:✓ AWS services initialized
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

You should see:
```
- ready started server on 0.0.0.0:3000
```

### 3. Open the Application

Open your browser to: http://localhost:3000

## Testing the Conversation

### Test 1: Basic Conversation Flow

1. **Select Language**: Choose English, Hindi, or Kannada
2. **Wait for Greeting**: The agent will greet you automatically
3. **Click "Speak"**: Click the microphone button
4. **Say Your Request**: "I want to know about government spending on education"
5. **Listen to Response**: Agent will acknowledge and ask for department
6. **Continue Conversation**: Keep speaking to answer agent's questions

### Test 2: Form Auto-Fill

Watch the form on the right side of the screen. As you speak, the agent will:
- Extract information from your speech
- Auto-fill form fields
- Show what information is still needed

### Test 3: Different Languages

Try the same conversation in Hindi:
1. Select "Hindi (हिंदी)"
2. Say: "मैं शिक्षा पर सरकारी खर्च के बारे में जानना चाहता हूं"
3. Agent will respond in Hindi

Or Kannada:
1. Select "Kannada (ಕನ್ನಡ)"
2. Say: "ನಾನು ಶಿಕ್ಷಣದ ಮೇಲೆ ಸರ್ಕಾರದ ಖರ್ಚಿನ ಬಗ್ಗೆ ತಿಳಿಯಲು ಬಯಸುತ್ತೇನೆ"
3. Agent will respond in Kannada

## Testing with the API Directly

### Test Script

Run the automated test:

```bash
cd backend
python test_conversation.py
```

This will:
1. Create a session
2. Get initial greeting
3. Have a multi-turn conversation
4. Show form updates
5. Display final form data

### Manual API Testing

Using curl or Postman:

```bash
# 1. Create session
curl -X POST http://localhost:8000/session/create \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'

# Response: {"session_id": "abc-123", ...}

# 2. Start conversation (use session_id from above)
curl -X POST http://localhost:8000/session/abc-123/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "", "language": "en"}'

# 3. Continue conversation
curl -X POST http://localhost:8000/session/abc-123/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to know about education spending", "language": "en"}'

# 4. Check form data
curl http://localhost:8000/form/abc-123
```

## What to Look For

### ✅ Good Signs

1. **Agent asks questions** - Not just echoing
2. **Form auto-fills** - Fields populate as you speak
3. **Natural conversation** - Feels like talking to a person
4. **Language consistency** - Agent speaks your language
5. **Progress tracking** - Agent knows what's missing

### ❌ Problems to Watch For

1. **Echo behavior** - If agent just repeats what you said, check:
   - Is `USE_MOCK_SERVICES=false` in `.env`?
   - Is Bedrock initialized? Check backend logs
   - Is `rti_agent_service` loaded?

2. **No greeting** - If no initial greeting:
   - Check browser console for errors
   - Check backend logs
   - Verify session was created

3. **Form not updating** - If form doesn't auto-fill:
   - Check network tab for API calls
   - Verify `/conversation` endpoint is called
   - Check `form_updates` in response

## Browser Requirements

- **Chrome** or **Edge** (for Web Speech API)
- **Microphone permission** must be granted
- **HTTPS** or **localhost** (required for microphone access)

## Troubleshooting

### "Speech recognition not supported"
- Use Chrome or Edge browser
- Check microphone permissions

### "No response from agent"
- Check backend is running
- Check AWS credentials in `.env`
- Look for errors in backend logs

### "Form not updating"
- Check network tab in browser DevTools
- Verify API calls are successful
- Check session_id is correct

### "Agent speaks wrong language"
- Verify language selector matches your speech
- Check language parameter in API calls
- Ensure language is one of: en, hi, kn

## Expected Behavior

### Complete Conversation Example

```
Agent: Hello! I'm your RTI assistant. What information would you like to request?

You: I want to know about government spending on education

Agent: Great! Which government department should I address this to?

You: Ministry of Education

Agent: Perfect! Now I need your name for the application.

You: My name is Rajesh Kumar

Agent: Thank you, Rajesh. What's your address?

You: 123 MG Road, Bangalore

Agent: Excellent! Your RTI application is almost complete. Let me confirm...
```

### Form Should Show

```
Information Sought: government spending on education
Department: Ministry of Education
Applicant Name: Rajesh Kumar
Address: 123 MG Road, Bangalore
```

## Performance Notes

- **First response**: May take 2-3 seconds (Bedrock cold start)
- **Subsequent responses**: Should be under 1 second
- **Speech recognition**: Starts within 1 second
- **TTS playback**: Starts immediately after processing

## Cost Monitoring

Check AWS costs:
```bash
# View Bedrock usage
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics BlendedCost --filter file://filter.json
```

Expected costs for testing:
- 10 conversations: ~$0.01-0.02
- 100 conversations: ~$0.10-0.20
- Very affordable for hackathon!

## Next Steps After Testing

Once basic conversation works:

1. **Add more RTI templates** - Common request types
2. **Improve extraction** - Better NLP for names/addresses
3. **Add validation** - Check address format, phone numbers
4. **Add examples** - Help users understand what to say
5. **Add confirmation** - Read back complete form before PDF

## Getting Help

If you encounter issues:

1. Check backend logs for errors
2. Check browser console for frontend errors
3. Verify AWS credentials are correct
4. Ensure all dependencies are installed
5. Try the test script first before frontend

## Success Criteria

You'll know it's working when:
- ✅ Agent greets you automatically
- ✅ Agent asks follow-up questions
- ✅ Form fills automatically as you speak
- ✅ Agent speaks back in your language
- ✅ Conversation feels natural, not robotic
- ✅ You can complete an RTI application by voice alone
