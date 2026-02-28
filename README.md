# RTI Voice Assistant

An AI-powered, accessibility-first voice assistant that enables persons with visual and motor disabilities to understand legal documents and independently complete RTI (Right to Information) applications in Indian languages.

## Features

- 🗣️ **Multilingual Voice Interaction**: English, Hindi, and Kannada support
- ♿ **Accessibility-First**: Screen reader compatible, keyboard navigation, voice-first UI
- 📝 **Guided RTI Form Completion**: Step-by-step assistance with legal simplification
- 📄 **Document Generation**: Submission-ready PDF and text formats
- 🔒 **Privacy Compliant**: DPDPA 2023 compliant with 24-hour data retention
- 💾 **Auto-Save**: Session management with progress persistence

## Architecture

### Tech Stack

- **Frontend**: Next.js (TypeScript) on AWS Amplify
- **Backend**: AWS Lambda (Python 3.11+)
- **LLM**: Amazon Bedrock (Claude 3 Haiku)
- **Speech-to-Text**: AI4Bharat IndicWhisper (containerized Lambda)
- **Text-to-Speech**: AWS Polly (Hindi/English) + gTTS (Kannada)
- **Database**: Amazon DynamoDB (sessions with TTL)
- **Storage**: Amazon S3 (documents with lifecycle policies)
- **API**: AWS API Gateway (REST/WebSocket)
- **Monitoring**: CloudWatch Logs + X-Ray

### AWS Services

- Amazon Bedrock - Legal reasoning and simplification
- AWS Lambda - Serverless compute
- DynamoDB - Session state with 24h TTL
- S3 - Temporary document storage
- API Gateway - REST/WebSocket APIs
- AWS Polly - Text-to-speech
- CloudWatch - Logging and monitoring
- AWS Amplify - Frontend hosting
- AWS KMS - Encryption

## Project Structure

```
rti-voice-assistant/
├── backend/                 # AWS Lambda functions
│   ├── voice-service/      # Speech processing
│   ├── legal-service/      # Legal guidance with Bedrock
│   ├── form-service/       # RTI form processing
│   ├── session-service/    # Session management
│   └── privacy-service/    # DPDPA compliance
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Next.js pages
│   │   └── lib/           # Utilities
│   └── public/            # Static assets
├── infrastructure/         # IaC templates
│   ├── cloudformation/    # CloudFormation templates
│   └── sam/               # AWS SAM templates
└── docs/                  # Documentation
```

## Prerequisites

- AWS Account with appropriate credits
- AWS CLI configured
- Node.js 18+ and npm
- Python 3.11+
- Docker (for Lambda container images)
- AWS SAM CLI (optional, for local testing)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rti-voice-assistant
```

### 2. Set Up AWS Infrastructure

```bash
cd infrastructure
# Deploy using CloudFormation or SAM
aws cloudformation create-stack --stack-name rti-voice-assistant --template-body file://cloudformation/main.yaml
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your AWS resource ARNs
```

### 4. Deploy Backend Lambda Functions

```bash
cd backend
# Build and deploy Lambda functions
./deploy.sh
```

### 5. Deploy Frontend to Amplify

```bash
cd frontend
npm install
npm run build
# Deploy to Amplify (or use Amplify Console)
```

## Development

### Local Development

```bash
# Backend (using SAM local)
cd backend
sam local start-api

# Frontend
cd frontend
npm run dev
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Privacy & Compliance

This application complies with India's Digital Personal Data Protection Act (DPDPA) 2023:

- ✅ Explicit consent collection
- ✅ End-to-end encryption (AWS KMS)
- ✅ 24-hour maximum data retention (DynamoDB TTL + S3 lifecycle)
- ✅ Audit logging (CloudWatch)
- ✅ Data deletion on request

## License

[License Type] - See LICENSE file for details

## Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## Support

For issues and questions, please open a GitHub issue or contact [support email].
