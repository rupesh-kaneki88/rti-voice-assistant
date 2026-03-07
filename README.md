# RTI Voice Assistant

An AI-powered, accessibility-first voice assistant that enables persons with visual and motor disabilities to understand legal documents and independently complete RTI (Right to Information) applications in Indian languages.

## Features

- 🗣️ **Multilingual Voice Interaction**: Full conversational support for English, Hindi, and Kannada.
- ⚡ **High-Speed Responses**: Powered by Groq for near-instantaneous English conversation.
- 🧠 **Intelligent & Robust**: A smart fallback system (Groq → Gemini → Rule-based) ensures the agent is always responsive.
- ♿ **Accessibility-First**: Designed for voice-only interaction, with screen reader compatibility and clear audio feedback.
- 📝 **Guided Form Completion**: The AI agent guides users step-by-step through the RTI application.
- 📄 **Document Generation**: Generates a submission-ready PDF of the completed RTI application.
- 🔒 **Privacy Compliant**: Sessions and data are stored temporarily in DynamoDB with a 24-hour TTL.

---

## Our Journey: From an All-AWS Plan to a Faster, More Robust Hybrid Approach

For the hackathon community, we wanted to share a transparent look at our architectural evolution. Our journey highlights key challenges in rapid prototyping and how we pivoted to create a better, more resilient application.

### The Initial Plan: An All-AWS Architecture
Our initial goal was to build the entire application using AWS services. The core of our AI logic was planned around **AWS Bedrock (with Claude 3 Haiku)**. We also intended to use AWS Polly for all Text-to-Speech (TTS) needs.

### The Hurdles: Why We Pivoted

1.  **The AWS Bedrock Payment Wall**: A significant roadblock was the `INVALID_PAYMENT_INSTRUMENT` error when enabling Bedrock. This required a specific type of credit card and couldn't be resolved with standard payment methods like UPI, which is a common issue for developers and hackathon participants in India. This completely halted our development on the core AI feature.

2.  **Real-Time Conversation Latency**: In our initial tests with Bedrock, we found that the response times, while acceptable, were not ideal for a truly real-time, natural-feeling voice conversation. Delays of even 2-3 seconds can disrupt the user experience.

3.  **Limited Language Support for TTS**: We discovered that **AWS Polly does not offer a voice for the Kannada language**. This was a major issue for our goal of providing comprehensive multilingual support.

### The Solution: A Hybrid, Best-of-Breed Approach

We pivoted to a hybrid model that leverages third-party services with excellent free tiers, solving all our previous issues.

1.  **Groq for Unmatched Speed**: For English, our primary LLM is **Groq**, running LLaMA 3.1. It is incredibly fast (often >500 tokens/sec), providing the near-instant responses needed for a fluid conversation.

2.  **Gemini for Superior Multilingual Support**: For **Hindi and Kannada**, we use **Google's Gemini 1.5 Flash**. It has exceptional multilingual capabilities and provides high-quality, nuanced responses in these languages.

3.  **gTTS for Kannada Voice**: To solve the TTS problem, we integrated the `gTTS` (Google Text-to-Speech) library, which provides a clear and natural-sounding voice for Kannada, ensuring a first-class experience for Kannada-speaking users.

### The Result: A Faster, More Robust System

This new architecture isn't just a workaround; it's an upgrade. We now have a **triple-fallback system** that makes our application incredibly robust:

-   **English Flow**: `Groq` → `Gemini` (if Groq fails) → `Rule-based` (if both fail)
-   **Hindi/Kannada Flow**: `Gemini` → `Groq` (if Gemini fails) → `Rule-based` (if both fail)

This ensures that the user always gets a response, making the system reliable even if one of the LLM providers is down. Best of all, the generous free tiers from Groq and Google allowed us to build this entire system without being blocked by payment issues.

---

## Tech Stack

- **Frontend**: Next.js (TypeScript)
- **Backend**: FastAPI (Python)
- **Primary LLM (English)**: Groq (LLaMA 3.1 70B)
- **Fallback & Multilingual LLM**: Google Gemini 1.5 Flash
- **Text-to-Speech**: AWS Polly (English/Hindi) & gTTS (Kannada)
- **Database**: Amazon DynamoDB (for session storage with 24h TTL)
- **Storage**: Amazon S3 (for temporary document storage)

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Groq API Key
- Gemini API Key

### 1. Clone the Repository
```bash
git clone <repository-url>
cd rti-voice-assistant
```

### 2. Configure Environment Variables
Create a `.env` file in the `backend` directory and add your API keys:
```bash
# backend/.env
GROQ_API_KEY=gsk_your_key_here
GEMINI_API_KEY=AIza_your_key_here
```

### 3. Install Dependencies & Run

#### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### Frontend (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```

### 4. Open the App
Navigate to `http://localhost:3000` in your browser.
