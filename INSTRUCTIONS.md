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

The system uses **DynamoDB** to store session data, including the conversation history and the current agent mode.

### Conversation Flow & Agent Modes

The agent operates in one of three modes: `initial`, `knowledge`, or `form-filling`. This creates a flexible and intuitive user experience.

#### 1. Initial Mode
- **Trigger:** A new session starts in this mode.
- **Agent's Action:** The agent asks the user to choose a path: get information or create an application.
- **User's Action:** Respond with your choice (e.g., "I want to know about RTI" or "Let's start an application").

#### 2. Knowledge Mode
- **Trigger:** The user chooses to "get information".
- **Agent's Action:** The agent acts as a specialized "RTI Sahayak".
    - It answers questions strictly related to the RTI Act.
    - It will politely decline to answer off-topic questions.
    - It will **not** try to fill any form fields.
    - The frontend UI adapts to a full-screen chat experience.
- **User's Action:** Ask any question about the RTI process, rules, or definitions.
- **Switching to Form-Filling:** At any time, you can say "Okay, let's file an application about this" to seamlessly switch modes. The agent will use the context of your questions to start the application.

#### 3. Form-Filling Mode
- **Trigger:** The user chooses to "create an application" or switches from `knowledge` mode.
- **Agent's Action:**
    - The agent guides you step-by-step through the RTI form.
    - It helps you collaboratively draft a detailed and effective query for the `information_sought` field.
    - It asks for one piece of information at a time until the form is complete.
- **User's Action:** Answer the agent's questions to fill the form.

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

### Frontend Voice Controls
The frontend now includes enhanced controls for a more accessible voice interaction:
-   **Stop Speaking:** During the agent's response, you can click the main voice button again to immediately stop the agent from speaking.
-   **Repeat Last Message:** After the agent has finished speaking, a "Repeat" button (or similar UI element) will appear. Click it to hear the agent's last message again.
-   **Toggle Speech Speed:** A "Speed" button (or similar UI element) allows you to cycle through different speech speeds (e.g., normal, slow, slower) for the agent's responses. This helps users who prefer a slower pace.
