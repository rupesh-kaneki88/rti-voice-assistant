# RTI Voice Assistant - Deployment Guide

## Prerequisites

1. **AWS Account** with appropriate credits
2. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```
3. **Node.js 18+** and npm
4. **Python 3.11+**
5. **Docker** (for Lambda container images)
6. **AWS SAM CLI** (optional, for local testing)

## Step 1: Deploy AWS Infrastructure

### Using CloudFormation

```bash
cd infrastructure/cloudformation
chmod +x deploy.sh
./deploy.sh dev  # or staging, prod
```

This will create:
- DynamoDB tables (sessions, consent) with TTL
- S3 buckets (documents, knowledge base) with lifecycle policies
- IAM roles for Lambda execution
- KMS encryption key
- API Gateway REST API
- CloudWatch Log Groups

### Verify Deployment

```bash
aws cloudformation describe-stacks --stack-name rti-voice-assistant --region us-east-1
```

## Step 2: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with values from CloudFormation outputs:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name rti-voice-assistant \
     --query 'Stacks[0].Outputs' \
     --output table
   ```

3. Fill in the following values:
   - `DYNAMODB_SESSIONS_TABLE`
   - `DYNAMODB_CONSENT_TABLE`
   - `S3_DOCUMENTS_BUCKET`
   - `S3_KNOWLEDGE_BASE_BUCKET`
   - `AWS_ACCOUNT_ID`

## Step 3: Deploy Backend Lambda Functions

### Prepare Lambda Layers

```bash
cd backend
pip install -r requirements.txt -t ./layer/python
cd layer
zip -r ../lambda-layer.zip .
cd ..
```

### Deploy Individual Services

Each Lambda function will be deployed separately in subsequent tasks:

1. **Voice Service** (Task 2)
2. **Legal Service** (Task 7)
3. **Form Service** (Task 6)
4. **Session Service** (Task 5)
5. **Privacy Service** (Task 9)

## Step 4: Upload Knowledge Base Content

Upload RTI rights and procedures to S3:

```bash
aws s3 cp docs/rti-knowledge-base/ \
  s3://YOUR-KNOWLEDGE-BASE-BUCKET/ \
  --recursive
```

## Step 5: Deploy Frontend to AWS Amplify

### Option A: Using Amplify Console (Recommended)

1. Go to AWS Amplify Console
2. Click "New app" → "Host web app"
3. Connect your Git repository
4. Configure build settings:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd frontend
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: frontend/.next
       files:
         - '**/*'
     cache:
       paths:
         - frontend/node_modules/**/*
   ```
5. Add environment variables in Amplify Console
6. Deploy

### Option B: Manual Deployment

```bash
cd frontend
npm install
npm run build

# Deploy to S3 + CloudFront (manual setup required)
aws s3 sync .next/static s3://your-frontend-bucket/static
```

## Step 6: Configure API Gateway

### Add Lambda Integrations

For each Lambda function, create API Gateway integration:

```bash
# Example for voice service
aws apigateway put-integration \
  --rest-api-id YOUR_API_ID \
  --resource-id YOUR_RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:REGION:lambda:path/2015-03-31/functions/LAMBDA_ARN/invocations
```

### Deploy API Stage

```bash
aws apigateway create-deployment \
  --rest-api-id YOUR_API_ID \
  --stage-name dev
```

## Step 7: Enable CloudWatch Monitoring

### Create CloudWatch Dashboard

```bash
aws cloudwatch put-dashboard \
  --dashboard-name rti-voice-assistant \
  --dashboard-body file://infrastructure/cloudwatch-dashboard.json
```

### Set Up Alarms

```bash
# Lambda error alarm
aws cloudwatch put-metric-alarm \
  --alarm-name rti-lambda-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

## Step 8: Test the Deployment

### Test Backend APIs

```bash
# Test session creation
curl -X POST https://YOUR_API_URL/session/create \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'

# Test health check
curl https://YOUR_API_URL/health
```

### Test Frontend

1. Navigate to Amplify URL
2. Test voice recording
3. Test form submission
4. Verify accessibility with screen reader

## Step 9: Set Up Cost Monitoring

```bash
# Create budget alert
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://infrastructure/budget.json
```

## Troubleshooting

### Lambda Cold Starts

If IndicWhisper Lambda has slow cold starts:
```bash
# Enable provisioned concurrency
aws lambda put-provisioned-concurrency-config \
  --function-name voice-service \
  --provisioned-concurrent-executions 1 \
  --qualifier LATEST
```

### DynamoDB Throttling

If you see throttling errors:
```bash
# Switch to on-demand billing
aws dynamodb update-table \
  --table-name rti-sessions-dev \
  --billing-mode PAY_PER_REQUEST
```

### S3 Lifecycle Not Working

Verify lifecycle policy:
```bash
aws s3api get-bucket-lifecycle-configuration \
  --bucket YOUR_DOCUMENTS_BUCKET
```

## Rollback

To rollback infrastructure:
```bash
aws cloudformation delete-stack --stack-name rti-voice-assistant
```

## Production Checklist

- [ ] Enable AWS WAF on API Gateway
- [ ] Set up CloudFront for frontend
- [ ] Enable X-Ray tracing on all Lambdas
- [ ] Configure backup for DynamoDB
- [ ] Set up SNS alerts for errors
- [ ] Enable VPC for Lambda functions (optional)
- [ ] Configure custom domain for API Gateway
- [ ] Set up CI/CD pipeline
- [ ] Enable AWS Config for compliance
- [ ] Review IAM policies for least privilege

## Cost Optimization

1. **Lambda**: Use ARM64 architecture for 20% cost savings
2. **DynamoDB**: Use on-demand billing for prototype
3. **S3**: Enable Intelligent-Tiering
4. **Bedrock**: Use Claude Haiku (cheapest model)
5. **API Gateway**: Enable caching for repeated requests

## Next Steps

After infrastructure is deployed:
1. Proceed to Task 2: Implement Voice Service Lambda
2. Test each service incrementally
3. Monitor CloudWatch Logs for errors
4. Iterate based on user feedback
