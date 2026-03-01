# RTI Voice Assistant - Full Deployment Guide

Complete guide to deploy the fully functional prototype with AWS services.

## Prerequisites

- Python 3.11+
- AWS Account with $100 credits
- AWS CLI configured with credentials

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

## Step 3: Enable Amazon Bedrock

1. Go to [AWS Console](https://console.aws.amazon.com/bedrock)
2. Navigate to **Amazon Bedrock** service
3. Click **Model access** in the left sidebar
4. Click **Manage model access**
5. Find **Claude 3 Haiku** and check the box
6. Click **Request model access**
7. Wait for approval (usually instant)

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
    "bedrock": true,
    "polly": true,
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
- ✅ Kannada (uses Hindi voice)
- Cost: ~$0.004/1000 characters

### 3. Legal Guidance (Amazon Bedrock - Claude 3 Haiku)
- ✅ RTI rights explanation
- ✅ Legal text simplification
- ✅ Multilingual support
- Cost: ~$0.00025/1000 tokens (very cheap!)

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

### Test Legal Guidance

```bash
curl -X POST "http://localhost:8000/guidance/explain?language=hi"
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
| Bedrock (Haiku) | $0.00025/1K tokens | ~400M tokens |
| DynamoDB | $0.01/day | ~3,000 days |
| S3 | $0.01/day | ~3,000 days |

**Total estimated runtime: 2-3 months with moderate usage**

## Troubleshooting

### "Bedrock not accessible"
- Make sure you enabled Claude 3 Haiku in Bedrock console
- Check region is set to `us-east-1` for Bedrock

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

## Fallback to Mock Services

If AWS services fail, the app automatically falls back to mock responses. To force mock mode:

```bash
# In .env file
USE_MOCK_SERVICES=true
```

## Next Steps

1. ✅ Backend fully functional with AWS
2. 🔄 Build frontend (Next.js)
3. 🔄 Add PDF generation
4. 🔄 Deploy to production

## Cleanup (When Done)

To avoid charges after hackathon:

```bash
# Delete DynamoDB table
aws dynamodb delete-table --table-name rti-sessions-dev --region ap-south-1

# Delete S3 buckets
aws s3 rb s3://rti-documents-dev-ACCOUNT_ID --force
aws s3 rb s3://rti-audio-dev-ACCOUNT_ID --force
```

## Support

If you encounter issues:
1. Check CloudWatch Logs for errors
2. Verify AWS credentials: `aws sts get-caller-identity`
3. Check service quotas in AWS Console
