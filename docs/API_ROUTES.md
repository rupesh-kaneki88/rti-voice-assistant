# RTI Voice Assistant - API Routes

## HTTP API Endpoint

Base URL: `https://{api-id}.execute-api.ap-south-1.amazonaws.com/dev`

## Route Syntax

HTTP API uses `{proxy+}` for catch-all routes, NOT `*`

✅ Correct: `/voice/{proxy+}`
❌ Wrong: `/voice/*`

## Available Routes

### Voice Service

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/voice/transcribe` | Speech-to-text transcription |
| POST | `/voice/synthesize` | Text-to-speech synthesis |
| ANY | `/voice/{proxy+}` | Catch-all for voice operations |

### Session Service

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/session/create` | Create new session |
| GET | `/session/{sessionId}` | Get session details |
| PUT | `/session/{sessionId}` | Update session |
| DELETE | `/session/{sessionId}` | Delete session |
| ANY | `/session/{proxy+}` | Catch-all for session operations |

### Form Service

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/form/update` | Update form field |
| POST | `/form/generate` | Generate RTI document |
| GET | `/form/{sessionId}` | Get form data |
| ANY | `/form/{proxy+}` | Catch-all for form operations |

### Legal Service

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/legal/guidance` | Get legal guidance |
| GET | `/legal/rti-rights` | Get RTI rights explanation |
| ANY | `/legal/{proxy+}` | Catch-all for legal operations |

### Health Check

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | API health check |

## Creating Routes in AWS Console

### Manual Route Creation

1. Go to **API Gateway Console**
2. Select your HTTP API
3. Click **"Routes"** in left menu
4. Click **"Create"**

#### For specific routes:
- Route: `POST /voice/transcribe`
- Integration: Select Lambda function

#### For catch-all routes:
- Route: `ANY /voice/{proxy+}`
- Integration: Select Lambda function

### Using AWS CLI

```bash
# Create specific route
aws apigatewayv2 create-route \
  --api-id YOUR_API_ID \
  --route-key "POST /voice/transcribe" \
  --target "integrations/YOUR_INTEGRATION_ID" \
  --region ap-south-1

# Create catch-all route (use {proxy+})
aws apigatewayv2 create-route \
  --api-id YOUR_API_ID \
  --route-key "ANY /voice/{proxy+}" \
  --target "integrations/YOUR_INTEGRATION_ID" \
  --region ap-south-1
```

## Path Parameters

### Single Parameter
Route: `/session/{sessionId}`
Example: `/session/abc123`

### Greedy Parameter (Catch-all)
Route: `/voice/{proxy+}`
Examples:
- `/voice/transcribe`
- `/voice/synthesize`
- `/voice/anything/nested/path`

## CORS Configuration

CORS is automatically configured in the HTTP API:
- **Allow Origins**: `*` (all origins)
- **Allow Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allow Headers**: `*` (all headers)
- **Max Age**: 300 seconds

## Testing Routes

### Using curl

```bash
# Health check
curl https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/dev/health

# Transcribe audio
curl -X POST https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/dev/voice/transcribe \
  -H "Content-Type: application/json" \
  -d '{"audio": "base64_encoded_audio", "language": "hi"}'

# Create session
curl -X POST https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/dev/session/create \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'
```

### Using AWS CLI

```bash
# Invoke via API Gateway
aws apigatewayv2 invoke-api \
  --api-id YOUR_API_ID \
  --stage dev \
  --path /health \
  --region ap-south-1
```

## Deployment

Routes are automatically deployed when using CloudFormation:

```bash
cd infrastructure/cloudformation
./deploy.sh dev
```

To deploy routes separately:

```bash
aws cloudformation create-stack \
  --stack-name rti-api-routes \
  --template-body file://api-routes.yaml \
  --parameters \
    ParameterKey=HttpApiId,ParameterValue=YOUR_API_ID \
    ParameterKey=VoiceServiceLambdaArn,ParameterValue=YOUR_LAMBDA_ARN \
  --region ap-south-1
```

## Troubleshooting

### Error: "One or more path parts appear to be invalid"

❌ **Wrong**: `/voice/*`
✅ **Correct**: `/voice/{proxy+}`

HTTP API uses `{proxy+}` for greedy path parameters, not `*`.

### Route Not Working

1. Check integration is attached to route
2. Verify Lambda permissions for API Gateway
3. Check CloudWatch Logs for errors
4. Test Lambda function directly first

### CORS Issues

HTTP API handles CORS automatically. If issues persist:
1. Check CORS configuration in API settings
2. Verify `Access-Control-Allow-Origin` header in Lambda response
3. Test with OPTIONS request

## Next Steps

1. Deploy main infrastructure stack
2. Deploy Lambda functions
3. Deploy API routes stack
4. Test each endpoint
5. Update frontend with API URL
