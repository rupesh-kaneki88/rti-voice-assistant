# Groq + Gemini Setup Guide

## Why This Change?

✅ **Groq**: Super fast (tokens/sec), free tier, great for English
✅ **Gemini**: Excellent multilingual support, free tier, handles Hindi/Kannada better
✅ **No Payment Issues**: Both have generous free tiers
✅ **Faster**: Much faster than Bedrock
✅ **Cheaper**: Free for hackathon usage

---

## Setup Steps

### 1. Get Groq API Key (Primary - English)

1. Go to: https://console.groq.com
2. Sign up with Google/GitHub
3. Go to "API Keys" section
4. Click "Create API Key"
5. Copy the key (starts with `gsk_...`)

**Free Tier**:
- 30 requests/minute
- 6,000 tokens/minute
- Perfect for hackathon!

### 2. Get Gemini API Key (Fallback - Multilingual)

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Select "Create API key in new project" or use existing
5. Copy the key (starts with `AIza...`)

**Free Tier**:
- 60 requests/minute
- 1 million tokens/day
- Excellent for testing!

### 3. Update .env File

```bash
cd backend

# Edit .env file
nano .env  # or use any editor
```

Add your keys:
```bash
# LLM Configuration
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=llama-3.1-70b-versatile

GEMINI_API_KEY=AIza_your_actual_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### 4. Install New Dependencies

```bash
cd backend
pip install groq google-generativeai
```

Or install all:
```bash
pip install -r requirements.txt
```

### 5. Test the Setup

```bash
cd backend
python test_conversation.py
```

You should see:
```
✓ Primary LLM: Groq (llama-3.1-70b-versatile)
✓ Fallback LLM: Gemini (gemini-1.5-flash)
```

---

## How It Works

### Language-Based Routing

```python
if language in ["hi", "kn"]:
    # Use Gemini first (better for Indian languages)
    try:
        response = gemini.generate(...)
    except:
        response = groq.generate(...)  # Fallback to Groq
else:
    # Use Groq first (faster for English)
    try:
        response = groq.generate(...)
    except:
        response = gemini.generate(...)  # Fallback to Gemini
```

### Fallback Chain

```
English:  Groq → Gemini → Rule-based
Hindi:    Gemini → Groq → Rule-based
Kannada:  Gemini → Groq → Rule-based
```

---

## Model Comparison

| Feature | Groq (LLaMA 3.1 70B) | Gemini 1.5 Flash |
|---------|---------------------|------------------|
| Speed | ⚡ Super fast | 🚀 Fast |
| English | ✅ Excellent | ✅ Excellent |
| Hindi | ✅ Good | ✅ Excellent |
| Kannada | ⚠️ Limited | ✅ Excellent |
| Free Tier | 30 req/min | 60 req/min |
| Cost | Free | Free |

---

## Strict Prompting

The new system uses strict prompts:

```
CRITICAL RULES - YOU MUST FOLLOW THESE:
1. Respond ONLY in [language]
2. Ask ONLY ONE question at a time
3. Keep your response under 3 sentences
4. NEVER give legal advice
5. Focus ONLY on collecting missing form fields
```

This ensures:
- ✅ Concise responses
- ✅ Focused conversation
- ✅ No legal liability
- ✅ Better user experience

---

## Testing Different Languages

### English
```bash
# Should use Groq
curl -X POST http://localhost:8000/session/abc/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "I want education info", "language": "en"}'
```

### Hindi
```bash
# Should use Gemini
curl -X POST http://localhost:8000/session/abc/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "मुझे शिक्षा की जानकारी चाहिए", "language": "hi"}'
```

### Kannada
```bash
# Should use Gemini
curl -X POST http://localhost:8000/session/abc/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "ನನಗೆ ಶಿಕ್ಷಣದ ಮಾಹಿತಿ ಬೇಕು", "language": "kn"}'
```

---

## Troubleshooting

### "Groq client not initialized"
- Check GROQ_API_KEY in .env
- Verify key starts with `gsk_`
- Run: `pip install groq`

### "Gemini client not initialized"
- Check GEMINI_API_KEY in .env
- Verify key starts with `AIza`
- Run: `pip install google-generativeai`

### "No LLM providers available"
- Both keys missing or invalid
- System will use rule-based fallback
- Still works, just less smart

### Rate Limit Errors
- Groq: 30 req/min limit
- Gemini: 60 req/min limit
- Wait a minute and try again
- Or upgrade to paid tier (not needed for hackathon)

---

## Cost Comparison

### Old (Bedrock)
- ❌ Requires payment method
- ❌ $0.25 per 1M input tokens
- ❌ Payment issues with UPI
- ❌ Slower responses

### New (Groq + Gemini)
- ✅ Free tier (no payment needed)
- ✅ Groq: 30 req/min free
- ✅ Gemini: 60 req/min free
- ✅ Much faster responses
- ✅ Better multilingual support

**For 100 conversations**:
- Bedrock: ~$0.10-0.20
- Groq + Gemini: **$0.00** (free tier)

---

## Quick Start Commands

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Add API keys to .env
nano .env  # Add GROQ_API_KEY and GEMINI_API_KEY

# 3. Test
python test_conversation.py

# 4. Start server
python app.py

# 5. Test frontend
cd ../frontend
npm run dev
```

---

## API Key Security

⚠️ **Important**:
- Never commit .env file to git
- .env is already in .gitignore
- Don't share API keys publicly
- Regenerate keys if exposed

---

## Next Steps

1. Get both API keys (5 minutes)
2. Update .env file (1 minute)
3. Install dependencies (2 minutes)
4. Test conversation (1 minute)
5. Start building! 🚀

The system will automatically:
- Use Groq for English (fast)
- Use Gemini for Hindi/Kannada (better multilingual)
- Fallback to rule-based if both fail
- Keep responses short and focused
