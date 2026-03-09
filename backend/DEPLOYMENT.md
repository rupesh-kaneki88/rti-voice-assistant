# RTI Voice Assistant - Full Deployment Guide

Complete guide to deploy the fully functional prototype with AWS services.

## Prerequisites

- Python 3.11+
- AWS Account with $100 credits
- AWS CLI configured with credentials
- Groq API Key
- Gemini API Key

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Setup AWS Resources

Run the setup script to create all AWS resources:

```bash
python setup_aws.py
```

This will create:
- ✅ DynamoDB table (`rti-sessions-dev`) with TTL
- ✅ S3 buckets for documents and audio
- ✅ .env file with all configuration

## Step 3: Configure LLM API Keys

Ensure your `.env` file in the `backend` directory has your Groq and Gemini API keys:

```
GROQ_API_KEY=your_api_key_here
GEMINI_API_KEY=your_api_key_here
```

## Step 4: Test Locally

Start the server:

```bash
uvicorn app:app --reload
```

Run tests:

```bash
python test_api.py
```

Open browser:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Step 5: Verify AWS Integration

Check the health endpoint to see if AWS services are connected:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "mode": "aws",
  "services": {
    "rti_agent": true,
    "tts": true,
    "transcribe": true
  }
}
```

## Features Now Working

### 1. Speech-to-Text (AWS Transcribe)
- ✅ Hindi (hi-IN)
- ✅ English (en-IN)
- ✅ Kannada (kn-IN)
- Cost: ~$0.024/minute

### 2. Text-to-Speech (AWS Polly)
- ✅ Hindi (Aditi voice - Neural)
- ✅ English (Joanna voice - Neural)
- ✅ Kannada (uses gTTS)
- Cost: ~$0.004/1000 characters (Polly)

### 3. Legal Guidance (Groq & Gemini LLMs)
- ✅ RTI rights explanation
- ✅ Legal text simplification
- ✅ Multilingual support
- Cost: Varies by provider, generally low with free tiers.

### 4. Session Management (DynamoDB)
- ✅ Create/Read/Update/Delete sessions
- ✅ Auto-delete after 24 hours (TTL)
- ✅ Form data persistence
- Cost: ~$0.01/day

### 5. Document Storage (S3)
- ✅ Audio file storage
- ✅ Document storage
- ✅ Auto-delete after 24 hours
- Cost: ~$0.01/day

## Testing Real AWS Services

### Test Transcription

```bash
curl -X POST http://localhost:8000/voice/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "audio": "BASE64_ENCODED_AUDIO",
    "language": "hi"
  }'
```

### Test TTS

```bash
curl -X POST http://localhost:8000/voice/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "नमस्ते, मैं आरटीआई आवेदन करना चाहता हूं",
    "language": "hi"
  }'
```

### Test Conversation (LLM)

```bash
curl -X POST http://localhost:8000/session/create \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'

# Use the session_id from the response
SESSION_ID="your_session_id_here"

curl -X POST "http://localhost:8000/session/${SESSION_ID}/conversation" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the RTI Act?", "language": "en"}'
```

## Cost Monitoring

Monitor your AWS costs:

```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

## Estimated Costs

With $100 AWS credits and moderate usage:

| Service | Cost | Usage |
|---------|------|-------|
| Transcribe | $0.024/min | ~4,000 minutes |
| Polly | $0.004/1K chars | ~25M characters |
| Groq/Gemini | Free Tier | Generous free tiers |
| DynamoDB | $0.01/day | ~3,000 days |
| S3 | $0.01/day | ~3,000 days |

**Total estimated runtime: 2-3 months with moderate usage**

## Troubleshooting

### "DynamoDB table not found"
- Run `python setup_aws.py` again
- Check AWS region is `ap-south-1`

### "S3 bucket not found"
- Run `python setup_aws.py` again
- Bucket names include your AWS account ID

### "Services showing as mock"
- Check `.env` file exists
- Make sure `USE_MOCK_SERVICES=false`
- Restart the server

### LLM Provider Errors
- Ensure `GROQ_API_KEY` and `GEMINI_API_KEY` are correctly set in `.env`.
- Check API provider dashboards for rate limits or account issues.

## Fallback to Mock Services

If AWS services or LLM providers fail, the app automatically falls back to mock responses. To force mock mode:

```bash
# In .env file
USE_MOCK_SERVICES=true
```

## Next Steps

1. ✅ Backend fully functional with AWS
2. 🔄 Build frontend (Next.js)
3. 🔄 Add PDF generation
4. 🔄 Deploy to production

## Step 6: Deploy to AWS Lambda & API Gateway

This section outlines how to deploy the FastAPI application as a serverless function using AWS Lambda and expose it via Amazon API Gateway.

### 6.1. Install Deployment Dependencies

First, install `Mangum` which is an ASGI adapter for AWS Lambda:

```bash
pip install mangum
```

### 6.2. Create Lambda Entry Point

Create a file named `lambda_function.py` in your `backend` directory with the following content:

```python
# backend/lambda_function.py
from mangum import Mangum
from app import app

handler = Mangum(app)
```

### 6.3. Package Your Application (using Docker cp)

To ensure all dependencies are compiled for the Lambda (Linux) environment and to avoid shell parsing issues, we'll use `docker cp`.

```bash
# Navigate to the backend directory
cd backend

# Create a temporary directory for packaging
mkdir package

# Copy your application code and necessary files into the 'package' directory
cp -r app.py services shared rti_templates.py lambda_function.py llm .env requirements.txt package/

# Create a temporary Docker container (it will run 'tail -f /dev/null' to stay alive)
CONTAINER_ID=$(docker run -d public.ecr.aws/lambda/python:3.11 tail -f /dev/null)

# Copy the contents of your local 'package' directory into the container
# This command should be run from the 'backend' directory
docker cp package/. "${CONTAINER_ID}:/var/task"

# Install dependencies inside the container, directly into /var/task
docker exec "${CONTAINER_ID}" /bin/bash -c "pip install -r /var/task/requirements.txt -t /var/task"

# Copy the installed dependencies (and app code) back out to a new local directory
mkdir package_final
docker cp "${CONTAINER_ID}:/var/task/." package_final/

# Remove the temporary container
docker rm "${CONTAINER_ID}"

# Zip the contents of the final package directory
cd package_final
zip -r9 ../deployment_package.zip .
cd ..

# Clean up temporary directories
rm -rf package package_final
```

### 6.3.1. Upload Deployment Package to S3

Upload the generated `deployment_package.zip` to an S3 bucket. You can use the `rti-documents-dev-ACCOUNT_ID` bucket created by `setup_aws.py`, or create a dedicated bucket for Lambda code.

```bash
# Example: Upload to the documents bucket
aws s3 cp deployment_package.zip s3://rti-documents-dev-YOUR_AWS_ACCOUNT_ID/lambda/deployment_package.zip
```
*Note: Replace `YOUR_AWS_ACCOUNT_ID` with your actual AWS account ID.*

### 6.4. Deploy using CloudFormation

We will use the provided CloudFormation templates to deploy the Lambda function and API Gateway.

1.  **Navigate to the CloudFormation directory:**
    ```bash
    cd infrastructure/cloudformation
    ```
2.  **Deploy the stack:**
    ```bash
    aws cloudformation deploy \
      --template-file main.yaml \
      --stack-name rti-voice-assistant-backend \
      --capabilities CAPABILITY_NAMED_IAM \
      --parameter-overrides \
        DeploymentBucketName=rti-lambda-deploy-dev-{id} \
        DeploymentBucketKey=lambda/deployment_package.zip \
        GroqApiKey=your_groq_api_key \
        GeminiApiKey=your_api_key \
        # Ensure these API keys are securely managed and not hardcoded in production
    ```
    *Note: Replace `YOUR_AWS_ACCOUNT_ID` with your actual AWS account ID and `your_groq_api_key_here`/`your_gemini_api_key_here` with your actual API keys. For production, consider using AWS Secrets Manager for API keys.*

3.  **Get API Gateway Endpoint:** After successful deployment, the API Gateway endpoint URL will be available in the CloudFormation stack outputs. Look for `HttpApiUrl`.


### 6.5. Update Frontend Configuration

Once deployed, update your frontend's API endpoint to point to the new API Gateway URL.

## Cleanup (When Done)

To avoid charges after hackathon:

```bash
# Delete DynamoDB table
aws dynamodb delete-table --table-name rti-sessions-dev --region ap-south-1

# Delete S3 buckets
aws s3 rb s3://rti-documents-dev-ACCOUNT_ID --force
aws s3 rb s3://rti-audio-dev-ACCOUNT_ID --force

# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name rti-voice-assistant-backend
```

## Support

If you encounter issues:
1. Check CloudWatch Logs for errors
2. Verify AWS credentials: `aws sts get-caller-identity`
3. Check service quotas in AWS Console

