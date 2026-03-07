# Project Instructions and Documentation

This file contains a consolidated summary of the various instruction and documentation files from the project.

## QUICK_START

### Get API Keys (5 minutes)

#### Groq (Primary - English)
1. Go to: https://console.groq.com
2. Sign up with Google/GitHub
3. Click "API Keys" → "Create API Key"
4. Copy key (starts with `gsk_`)

#### Gemini (Fallback - Multilingual)
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy key (starts with `AIza`)

### Update .env (1 minute)
```bash
cd backend
nano .env  # or use any editor
```
Replace these lines:
```bash
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Install Dependencies (2 minutes)
```bash
cd backend
pip install -r requirements.txt
```

### Test and Run
1.  **Test Backend:** `cd backend && python test_conversation.py`
2.  **Start Backend:** `cd backend && python app.py`
3.  **Start Frontend:** `cd frontend && npm run dev`
4.  **Open in Browser:** `http://localhost:3000`

---

## HOW_IT_ALL_WORKS

The system uses **DynamoDB** to store conversations and automatically fills the form as users speak.

### Conversation Flow
1.  **User Speaks:** Frontend captures audio, transcribes it, and calls the backend.
2.  **Backend Processes:**
    *   Retrieves conversation history from DynamoDB.
    *   Adds the new user message.
    *   Extracts form data using the LLM.
    *   Generates an agent response.
    *   Saves the updated conversation and form data back to DynamoDB.
    *   Returns the agent's response and form updates to the frontend.
3.  **Frontend Updates:**
    *   Speaks the agent's response using TTS.
    *   Refreshes the form to display the auto-filled data.

### Key Files
*   **Backend:** `app.py`, `services/rti_agent_service.py`, `shared/aws_clients.py`
*   **Frontend:** `app/page.tsx`, `components/VoiceRecorderRealtime.tsx`, `components/RTIForm.tsx`

---

## GROQ_GEMINI_SETUP

This project uses Groq for fast English responses and Gemini for superior multilingual capabilities (Hindi, Kannada), with a fallback system.

### Architecture
*   **English:** Groq -> Gemini -> Rule-based
*   **Hindi/Kannada:** Gemini -> Groq -> Rule-based

This provides a fast, reliable, and free-tier-friendly solution without the payment issues encountered with AWS Bedrock.

---

## MIGRATION_SUMMARY

The project was migrated from AWS Bedrock to a dual-provider system (Groq + Gemini).

### Benefits
*   **Speed:** Responses are much faster (<1 second).
*   **Cost:** Utilizes generous free tiers, avoiding payment issues.
*   **Reliability:** Triple fallback ensures the agent always responds.
*   **Multilingual:** Better support for Indian languages via Gemini.

---

## CONVERSATION_AGENT_IMPLEMENTATION

A full conversational AI agent was implemented to guide users step-by-step through the RTI form, ask follow-up questions, and maintain context. This replaced the old "echo" behavior.

---

## TESTING_GUIDE

### Automated Test
```bash
cd backend
python test_conversation.py
```
This script runs a full conversation flow and verifies form updates.

### Manual Test
1.  Start backend and frontend.
2.  Open `http://localhost:3000`.
3.  Select a language and speak a request.
4.  Converse with the agent until the form is complete.
5.  Verify that the form auto-fills correctly.
