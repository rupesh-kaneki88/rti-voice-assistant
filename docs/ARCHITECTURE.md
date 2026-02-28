# RTI Voice Assistant - Architecture Documentation

## Overview

The RTI Voice Assistant is built on AWS serverless architecture, prioritizing accessibility, privacy compliance (DPDPA 2023), and cost-effectiveness for a hackathon/prototype environment.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Web Browser  │  │Screen Reader │  │   Keyboard   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                    Frontend (AWS Amplify)                         │
│                     Next.js + TypeScript                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Voice UI │ Accessibility │ Offline Mode │ Session Mgmt  │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │  API Gateway    │
                    │  (REST/WebSocket)│
                    └────────┬────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                      Lambda Functions                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Voice   │  │  Legal   │  │   Form   │  │ Session  │        │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼───────────────┘
        │             │             │             │
        │             │             │             │
┌───────┼─────────────┼─────────────┼─────────────┼───────────────┐
│       │             │             │             │                │
│  ┌────▼────┐   ┌───▼────┐   ┌───▼────┐   ┌────▼────┐          │
│  │ Indic   │   │Bedrock │   │   S3   │   │DynamoDB │          │
│  │Whisper  │   │Claude  │   │Documents│   │Sessions │          │
│  │Container│   │ Haiku  │   │  TTL   │   │  TTL    │          │
│  └─────────┘   └────────┘   └────────┘   └─────────┘          │
│                                                                  │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │  Polly  │   │  gTTS   │   │   KMS   │   │CloudWatch│        │
│  │ (Hindi) │   │(Kannada)│   │Encryption│   │  Logs   │        │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘        │
│                                                                  │
│                    AWS Services Layer                            │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer (AWS Amplify)

**Technology**: Next.js 14 with TypeScript

**Key Features**:
- Voice-first UI with minimal visual elements
- WCAG 2.1 AA compliant
- Screen reader optimized (ARIA labels)
- Keyboard navigation support
- Service worker for offline mode
- IndexedDB for local storage

**Hosting**: AWS Amplify with automatic CI/CD

### 2. API Gateway

**Type**: REST API + WebSocket API

**Features**:
- Request/response transformation
- CORS configuration
- Rate limiting and throttling
- API key management
- Custom domain support

**Endpoints**:
- `/session/*` - Session management
- `/voice/*` - Speech processing
- `/legal/*` - Legal guidance
- `/form/*` - RTI form operations
- `/health` - Health check

### 3. Lambda Functions

#### Voice Service Lambda
- **Runtime**: Python 3.11 (Container Image for IndicWhisper)
- **Memory**: 10GB
- **Timeout**: 15 minutes
- **Purpose**: Speech-to-text (IndicWhisper) and text-to-speech (Polly/gTTS)

#### Legal Service Lambda
- **Runtime**: Python 3.11
- **Memory**: 3GB
- **Timeout**: 30 seconds
- **Purpose**: Legal text simplification using Bedrock

#### Form Service Lambda
- **Runtime**: Python 3.11
- **Memory**: 2GB
- **Timeout**: 60 seconds
- **Purpose**: RTI form processing and PDF generation

#### Session Service Lambda
- **Runtime**: Python 3.11
- **Memory**: 512MB
- **Timeout**: 10 seconds
- **Purpose**: Session CRUD operations with DynamoDB

#### Privacy Service Lambda
- **Runtime**: Python 3.11
- **Memory**: 512MB
- **Timeout**: 10 seconds
- **Purpose**: Consent management and DPDPA compliance

### 4. Data Layer

#### DynamoDB Tables

**Sessions Table**:
```
Primary Key: sessionId (String)
GSI: userId-index
TTL: 24 hours
Attributes:
  - sessionId
  - userId
  - language
  - currentStep
  - formData (Map)
  - createdAt
  - lastActivity
  - ttl (Unix timestamp)
```

**Consent Table**:
```
Primary Key: userId (String)
Sort Key: timestamp (Number)
TTL: 24 hours
Attributes:
  - userId
  - purposes (List)
  - consentGiven (Boolean)
  - timestamp
  - ttl
```

#### S3 Buckets

**Documents Bucket**:
- Purpose: Store generated RTI PDFs/text files
- Lifecycle: Delete after 24 hours
- Encryption: SSE-S3
- Versioning: Enabled

**Knowledge Base Bucket**:
- Purpose: Store RTI rights, procedures, templates
- Lifecycle: No expiration
- Encryption: SSE-S3
- Access: Read-only for Lambda

### 5. AI/ML Services

#### IndicWhisper (Speech Recognition)
- **Deployment**: Lambda Container Image
- **Model**: AI4Bharat IndicWhisper
- **Languages**: Hindi, Kannada, English
- **Accuracy**: 90%+ for Indian languages

#### Amazon Bedrock (LLM)
- **Model**: Claude 3 Haiku
- **Use Cases**:
  - Legal text simplification
  - RTI rights explanation
  - Form field validation
  - Post-completion guidance

#### AWS Polly (TTS)
- **Voices**: Aditi (Hindi), Joanna (English)
- **Format**: MP3
- **Features**: Neural voices, SSML support

#### gTTS (TTS Fallback)
- **Purpose**: Free Kannada TTS
- **Quality**: Standard (not neural)

### 6. Security & Compliance

#### Encryption
- **At Rest**: AWS KMS for DynamoDB and S3
- **In Transit**: TLS 1.2+ for all API calls
- **Key Management**: AWS KMS with automatic rotation

#### DPDPA 2023 Compliance
- Explicit consent collection
- 24-hour data retention (DynamoDB TTL + S3 lifecycle)
- Audit logging (CloudWatch)
- Data deletion on request
- Encryption for sensitive data

#### IAM Policies
- Least privilege access
- Separate roles per Lambda function
- No hardcoded credentials

### 7. Monitoring & Logging

#### CloudWatch Logs
- Structured JSON logging
- Log retention: 30 days
- Log groups per Lambda function

#### CloudWatch Metrics
- Lambda invocations, errors, duration
- DynamoDB read/write capacity
- API Gateway requests, latency
- Custom metrics for speech processing

#### AWS X-Ray
- Distributed tracing
- Performance bottleneck identification
- Service map visualization

## Data Flow

### User Journey: RTI Application Submission

1. **User Opens App**
   - Frontend loads from Amplify
   - Service worker registers for offline mode
   - Session created via API Gateway → Session Lambda → DynamoDB

2. **User Speaks (Hindi)**
   - Audio captured in browser
   - Sent to API Gateway → Voice Lambda
   - IndicWhisper transcribes audio
   - Transcription returned to frontend

3. **Legal Guidance Request**
   - User asks "What is RTI?"
   - Request → Legal Lambda → Bedrock (Claude)
   - Simplified explanation generated
   - Response → Polly TTS → Audio playback

4. **Form Completion**
   - User provides applicant details
   - Each field → Form Lambda → Validation
   - Auto-save → Session Lambda → DynamoDB (with TTL)

5. **Document Generation**
   - User completes form
   - Form Lambda → ReportLab → PDF generation
   - PDF stored in S3 (24h lifecycle)
   - Pre-signed URL returned to user

6. **Document Verification**
   - PDF content → Bedrock → Summarization
   - Summary → Polly TTS → Audio read-back
   - User confirms or edits

7. **Cleanup**
   - After 24 hours: DynamoDB TTL deletes session
   - S3 lifecycle policy deletes PDF
   - CloudWatch logs retained for 30 days

## Scalability

### Horizontal Scaling
- Lambda: Automatic scaling (up to 1000 concurrent executions)
- DynamoDB: On-demand capacity mode
- API Gateway: Handles millions of requests

### Performance Optimization
- Lambda provisioned concurrency for IndicWhisper (reduce cold starts)
- DynamoDB DAX for caching (optional)
- CloudFront CDN for frontend
- API Gateway caching for repeated requests

## Cost Estimation

**Monthly costs for moderate usage (1000 users)**:
- Lambda: ~$50 (mostly IndicWhisper)
- DynamoDB: ~$10 (on-demand)
- S3: ~$5 (24h retention)
- Bedrock: ~$20 (Claude Haiku)
- Polly: ~$10
- API Gateway: ~$5
- **Total**: ~$100/month

**Covered by AWS credits for hackathon/prototype**

## Disaster Recovery

- DynamoDB: Point-in-time recovery enabled
- S3: Versioning enabled
- Lambda: Code stored in ECR/S3
- Infrastructure: CloudFormation templates in Git

## Future Enhancements

1. **Multi-region deployment** for lower latency
2. **VPC integration** for enhanced security
3. **Amazon Connect** for phone-based access
4. **Amazon Translate** for additional languages
5. **Amazon Comprehend** for sentiment analysis
6. **Step Functions** for complex workflows
7. **EventBridge** for event-driven architecture
