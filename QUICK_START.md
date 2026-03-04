# Quick Start - Get Running in 10 Minutes

## Step 1: Get API Keys (5 minutes)

### Groq (Primary - English)
1. Go to: https://console.groq.com
2. Sign up with Google/GitHub
3. Click "API Keys" → "Create API Key"
4. Copy key (starts with `gsk_`)

### Gemini (Fallback - Multilingual)
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy key (starts with `AIza`)

---

## Step 2: Update .env (1 minute)

```bash
cd backend
nano .env  # or use any editor
```

Replace these lines:
```bash
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

With your actual keys:
```bash
GROQ_API_KEY=gsk_abc123...
GEMINI_API_KEY=AIza_xyz789...
```

---

## Step 3: Install Dependencies (2 minutes)

```bash
cd backend
pip install groq google-generativeai
```

Or install everything:
```bash
pip install -r requirements.txt
```

---

## Step 4: Test Backend (1 minute)

```bash
cd backend
python test_conversation.py
```

Expected output:
```
✓ Primary LLM: Groq (llama-3.1-70b-versatile)
✓ Fallback LLM: Gemini (gemini-1.5-flash)

1. Creating session...
✓ Session created: abc-123

2. Getting initial greeting...
Agent: Hello! I'm your RTI assistant...

3. User: I want to know about government spending on education
Generating with Groq...
✓ Groq response: Great! Which government department...
```

---

## Step 5: Start Backend (30 seconds)

```bash
cd backend
python app.py
```

You should see:
```
✓ Primary LLM: Groq (llama-3.1-70b-versatile)
✓ Fallback LLM: Gemini (gemini-1.5-flash)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 6: Start Frontend (30 seconds)

In a new terminal:
```bash
cd frontend
npm run dev
```

You should see:
```
- ready started server on 0.0.0.0:3000
```

---

## Step 7: Test in Browser (30 seconds)

1. Open: http://localhost:3000
2. Select language (English/Hindi/Kannada)
3. Click microphone button
4. Say: "I want information about education"
5. Watch the magic happen! ✨

---

## What You Should See

### Voice Interaction
- Agent greets you automatically
- You speak, it transcribes
- Agent responds intelligently
- Speaks back to you

### Form Auto-Fill
- Fields populate as you speak
- Real-time updates
- No manual typing needed

### Conversation Flow
```
Agent: Hello! What information would you like?
You: "I want education info"
Agent: Great! Which department?
You: "Ministry of Education"
Agent: Perfect! What's your name?
... and so on
```

---

## Troubleshooting

### "Groq client not initialized"
- Check GROQ_API_KEY in .env
- Make sure key starts with `gsk_`
- Run: `pip install groq`

### "Gemini client not initialized"
- Check GEMINI_API_KEY in .env
- Make sure key starts with `AIza`
- Run: `pip install google-generativeai`

### "No LLM providers available"
- Both keys missing or invalid
- System will use rule-based fallback
- Still works, just less smart

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
python app.py --port 8001
```

### Frontend won't start
```bash
# Install dependencies first
cd frontend
npm install

# Then start
npm run dev
```

---

## Testing Different Languages

### English (Uses Groq)
1. Select "English" in UI
2. Speak in English
3. Should be super fast!

### Hindi (Uses Gemini)
1. Select "Hindi (हिंदी)" in UI
2. Speak in Hindi
3. Better multilingual support!

### Kannada (Uses Gemini)
1. Select "Kannada (ಕನ್ನಡ)" in UI
2. Speak in Kannada
3. Excellent language support!

---

## What's Working

✅ Voice input (Web Speech API)
✅ Conversation with LLM (Groq/Gemini)
✅ Form auto-fill
✅ Text-to-speech (Polly/gTTS)
✅ PDF generation
✅ Multilingual support
✅ Session persistence (DynamoDB)

---

## What's Next

1. **Fix DynamoDB schema** (if needed)
   ```bash
   cd backend
   python check_dynamodb.py
   ```

2. **Test complete flow**
   - Create RTI application
   - Generate PDF
   - Download document

3. **Prepare for demo**
   - Test all 3 languages
   - Practice conversation flow
   - Show form auto-fill

---

## Demo Script

For hackathon presentation:

1. **Show problem**: "Complex RTI forms are hard for visually impaired"
2. **Show solution**: "Just speak naturally"
3. **Live demo**:
   - Select Hindi
   - Speak: "मुझे शिक्षा की जानकारी चाहिए"
   - Show form auto-filling
   - Generate PDF
4. **Show features**:
   - Multilingual (3 languages)
   - Voice-first (accessibility)
   - Auto-fill (no typing)
   - Fast (Groq/Gemini)
5. **Show tech**:
   - Groq for speed
   - Gemini for multilingual
   - DynamoDB for storage
   - Next.js for UI

---

## Cost for Hackathon

**Total: $0.00** (Free tier)

- Groq: 30 req/min free
- Gemini: 60 req/min free
- DynamoDB: Free tier (25GB)
- S3: Free tier (5GB)
- Polly: Free tier (5M chars/month)

Perfect for hackathon! 🎉

---

## Need Help?

Check these files:
- `GROQ_GEMINI_SETUP.md` - Detailed setup
- `HOW_IT_ALL_WORKS.md` - Architecture
- `MIGRATION_SUMMARY.md` - What changed
- `FIX_ISSUES.md` - Troubleshooting

Or just ask! 😊

---

## Success Checklist

- [ ] Got Groq API key
- [ ] Got Gemini API key
- [ ] Updated .env file
- [ ] Installed dependencies
- [ ] Backend starts successfully
- [ ] Frontend starts successfully
- [ ] Can speak and get response
- [ ] Form auto-fills
- [ ] Can generate PDF
- [ ] Tested all 3 languages

Once all checked, you're ready to demo! 🚀
