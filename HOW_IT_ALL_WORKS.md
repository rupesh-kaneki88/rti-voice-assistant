# How the RTI Voice Assistant Works - Complete Flow

## Overview

The system uses **DynamoDB** (not Redis) to store conversations and automatically fills the form as users speak. Here's the complete flow:

---

## 1. Storage: DynamoDB (Not Redis!)

### Why DynamoDB, Not Redis?

✅ **DynamoDB Benefits**:
- Serverless (no server to manage)
- Built-in TTL (auto-delete after 24 hours for DPDPA compliance)
- Pay per request (cheaper for hackathon)
- Persistent storage
- AWS-native integration

❌ **Redis Would Be**:
- Requires server management
- More expensive
- Overkill for this use case
- Need manual TTL implementation

### What's Stored in DynamoDB

```json
{
  "session_id": "abc-123",
  "language": "en",
  "created_at": "2024-01-01T10:00:00",
  "ttl": 1704196800,  // Auto-delete after 24 hours
  "conversation_history": [
    {"role": "assistant", "content": "Hello! I'm your RTI assistant..."},
    {"role": "user", "content": "I want info about education spending"},
    {"role": "assistant", "content": "Great! Which department?"},
    {"role": "user", "content": "Ministry of Education"}
  ],
  "form_data": {
    "information_sought": "government spending on education",
    "department": "Ministry of Education",
    "applicant_name": "",
    "address": ""
  }
}
```

---

## 2. Conversation Flow: How It Works

### Step 1: User Speaks

```
User: "I want to know about government spending on education"
```

**Frontend** (`VoiceRecorderRealtime.tsx`):
1. Web Speech API captures audio
2. Transcribes to text
3. Calls `/session/{id}/conversation` API

### Step 2: Backend Processes

**Backend** (`app.py` → `rti_agent_service.py`):

1. **Get conversation history** from DynamoDB
   ```python
   conversation_history = session_data.get('conversation_history', [])
   form_data = session_data.get('form_data', {})
   ```

2. **Add user message** to history
   ```python
   conversation_history.append({
       "role": "user",
       "content": "I want to know about government spending on education"
   })
   ```

3. **Extract form data** from message
   ```python
   # rti_agent_service.py - _extract_form_updates()
   updates = {
       'information_sought': "government spending on education",
       'department': "Ministry of Education"  # Auto-detected from "education"
   }
   ```

4. **Generate agent response** (Bedrock or rule-based)
   ```python
   agent_message = "Great! I understand you want information about government 
                    spending on education. Which government department should 
                    I address this to?"
   ```

5. **Add agent response** to history
   ```python
   conversation_history.append({
       "role": "assistant",
       "content": agent_message
   })
   ```

6. **Save everything** to DynamoDB
   ```python
   session_data['conversation_history'] = conversation_history
   session_data['form_data'] = {**form_data, **updates}
   save_session_to_db(session_data)
   ```

7. **Return to frontend**
   ```json
   {
     "agent_response": "Great! Which department?",
     "form_updates": {
       "information_sought": "government spending on education",
       "department": "Ministry of Education"
     },
     "is_complete": false
   }
   ```

### Step 3: Frontend Updates

**Frontend** (`VoiceRecorderRealtime.tsx`):
1. Receives agent response
2. Speaks it back via TTS
3. Triggers form refresh event
   ```typescript
   window.dispatchEvent(new CustomEvent('refreshForm'));
   ```

**Form Component** (`RTIForm.tsx`):
1. Listens for refresh event
2. Calls `/form/{session_id}` to get latest data
3. Updates form fields automatically

---

## 3. Form Auto-Fill: How Information is Extracted

### Extraction Logic (`rti_agent_service.py`)

```python
def _extract_form_updates(user_message, current_form_data):
    updates = {}
    
    # 1. Detect category and suggest department
    if "education" in message:
        updates['department'] = 'Ministry of Education'
    elif "health" in message:
        updates['department'] = 'Ministry of Health'
    
    # 2. Extract name
    if "my name is" in message:
        name = message.split("my name is")[1].strip()
        updates['applicant_name'] = name
    
    # 3. Extract address
    if "address" in message or "live at" in message:
        address = extract_after_pattern(message)
        updates['address'] = address
    
    # 4. Extract information request
    if len(message.split()) > 5 and not current_form_data.get('information_sought'):
        updates['information_sought'] = message
    
    return updates
```

### Example Extractions

| User Says | Extracted Field | Value |
|-----------|----------------|-------|
| "I want info about education spending" | `information_sought` | "education spending" |
| "Ministry of Education" | `department` | "Ministry of Education" |
| "My name is Rajesh Kumar" | `applicant_name` | "Rajesh Kumar" |
| "I live at 123 MG Road, Bangalore" | `address` | "123 MG Road, Bangalore" |

---

## 4. Complete Example Flow

### Conversation 1

```
Agent: Hello! What information would you like to request?

User: "I want to know about government spending on education"
  ↓
  Extract: information_sought = "government spending on education"
  Extract: department = "Ministry of Education" (auto-detected)
  ↓
Agent: "Great! I understand. Which department should I address this to?"

User: "Ministry of Education"
  ↓
  Confirm: department = "Ministry of Education"
  ↓
Agent: "Perfect! Now I need your name for the application."

User: "My name is Rajesh Kumar"
  ↓
  Extract: applicant_name = "Rajesh Kumar"
  ↓
Agent: "Thank you, Rajesh! What is your address?"

User: "123 MG Road, Bangalore"
  ↓
  Extract: address = "123 MG Road, Bangalore"
  ↓
Agent: "Excellent! Your RTI application is complete. Let me confirm..."
```

### Form State After Each Turn

**After Turn 1**:
```json
{
  "information_sought": "government spending on education",
  "department": "Ministry of Education",
  "applicant_name": "",
  "address": ""
}
```

**After Turn 2**:
```json
{
  "information_sought": "government spending on education",
  "department": "Ministry of Education",  // Confirmed
  "applicant_name": "",
  "address": ""
}
```

**After Turn 3**:
```json
{
  "information_sought": "government spending on education",
  "department": "Ministry of Education",
  "applicant_name": "Rajesh Kumar",  // Added
  "address": ""
}
```

**After Turn 4** (Complete!):
```json
{
  "information_sought": "government spending on education",
  "department": "Ministry of Education",
  "applicant_name": "Rajesh Kumar",
  "address": "123 MG Road, Bangalore"  // Added
}
```

---

## 5. UI Display: Real-Time Updates

### How Form Updates in Real-Time

1. **User speaks** → Voice component processes
2. **Backend extracts** → Returns `form_updates`
3. **Voice component** → Triggers `refreshForm` event
4. **Form component** → Listens for event
5. **Form component** → Calls API to get latest data
6. **Form fields** → Update automatically

### Visual Flow

```
┌─────────────────┐
│  User Speaks    │
│  "My name is    │
│   Rajesh"       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backend        │
│  Extracts:      │
│  name="Rajesh"  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Saves to       │
│  DynamoDB       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Returns to     │
│  Frontend       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Triggers       │
│  Form Refresh   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Form Fetches   │
│  Latest Data    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Name Field     │
│  Shows "Rajesh" │
└─────────────────┘
```

---

## 6. Key Files and Their Roles

### Backend

| File | Purpose |
|------|---------|
| `app.py` | Main API endpoints, conversation orchestration |
| `services/rti_agent_service.py` | Conversation logic, form extraction, Bedrock integration |
| `services/polly_service.py` | Text-to-speech |
| `rti_templates.py` | RTI category detection, department suggestions |
| `shared/aws_clients.py` | DynamoDB connection |

### Frontend

| File | Purpose |
|------|---------|
| `app/page.tsx` | Main page, session management |
| `components/VoiceRecorderRealtime.tsx` | Voice input, conversation display |
| `components/RTIForm.tsx` | Form display, auto-refresh |
| `lib/api.ts` | API client functions |

---

## 7. What Happens When You Fix AWS Issues

### Once Payment Method is Added

1. **Bedrock works** → Natural conversation
2. **Better extraction** → More accurate form filling
3. **Smarter responses** → Contextual understanding

### Once DynamoDB Schema is Fixed

1. **Conversations persist** → Survive page refresh
2. **Form data saves** → No data loss
3. **History maintained** → Agent remembers context

---

## 8. Testing the Complete Flow

### Test Script

```bash
cd backend
python test_conversation.py
```

### Expected Output

```
1. Creating session...
✓ Session created: abc-123

2. Getting initial greeting...
Agent: Hello! I'm your RTI assistant...

3. User: I want to know about government spending on education
Agent: Great! Which government department should I address this to?
Form updates: {'information_sought': '...', 'department': 'Ministry of Education'}

4. User: Ministry of Education
Agent: Perfect! Now I need your name for the application.
Form updates: {'department': 'Ministry of Education'}

5. User: My name is Rajesh Kumar
Agent: Thank you, Rajesh! What is your address?
Form updates: {'applicant_name': 'Rajesh Kumar'}

6. Checking form data...
Form data: {
  "information_sought": "government spending on education",
  "department": "Ministry of Education",
  "applicant_name": "Rajesh Kumar",
  "address": ""
}
```

---

## Summary

✅ **Storage**: DynamoDB (not Redis) - serverless, TTL, persistent
✅ **Conversations**: Stored in `conversation_history` array
✅ **Form Filling**: Automatic extraction from natural language
✅ **UI Updates**: Real-time via event system
✅ **Persistence**: Survives page refresh (once DynamoDB is fixed)

**No Redis needed!** Everything works with DynamoDB + in-memory fallback.
