# Voice Service Lambda

Speech-to-text transcription service using AI4Bharat IndicWhisper for Indian languages (Hindi, Kannada) and OpenAI Whisper for English.

## Features

- **IndicWhisper**: High-accuracy transcription for Hindi and Kannada
- **OpenAI Whisper**: Fallback for English transcription
- **Auto-detection**: Automatically detects language from audio
- **Container-based**: Deployed as Lambda container image (up to 10GB)
- **Optimized**: Lazy loading to reduce cold start time

## Architecture

```
Audio Input (base64)
    ↓
Lambda Handler
    ↓
Language Detection
    ↓
┌─────────────┬─────────────┐
│ Hindi/Kannada│   English   │
│ IndicWhisper │   Whisper   │
└─────────────┴─────────────┘
    ↓
Transcription Result
```

## API

### Endpoint: POST /voice/transcribe

**Request:**
```json
{
  "audio": "base64_encoded_audio_data",
  "language": "hi"  // optional: en, hi, kn
}
```

**Response:**
```json
{
  "text": "नमस्ते, मैं आरटीआई आवेदन करना चाहता हूं",
  "confidence": 0.95,
  "language": "hi",
  "timestamp": "request-id"
}
```

## Deployment

### Prerequisites

1. Docker installed
2. AWS CLI configured
3. ECR repository access
4. Lambda execution role created

### Deploy

```bash
chmod +x deploy.sh
./deploy.sh latest
```

This will:
1. Build Docker image with IndicWhisper model
2. Push to Amazon ECR
3. Create/update Lambda function
4. Configure timeout (15 min) and memory (10GB)

### Local Testing

```bash
# Build image
docker build -t rti-voice-service .

# Run locally
docker run -p 9000:8080 rti-voice-service

# Test
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d @test_event.json
```

## Configuration

### Environment Variables

- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)
- `AWS_REGION`: AWS region (ap-south-1)

### Lambda Configuration

- **Timeout**: 900 seconds (15 minutes)
- **Memory**: 10240 MB (10 GB)
- **Runtime**: Python 3.11 (container)
- **Architecture**: x86_64

## Models

### IndicWhisper
- **Model**: vasista22/whisper-hindi-large-v2
- **Languages**: Hindi, Kannada
- **Accuracy**: 90%+
- **Size**: ~3GB

### OpenAI Whisper
- **Model**: base
- **Language**: English
- **Accuracy**: 85%+
- **Size**: ~140MB

## Performance

- **Cold Start**: ~30-60 seconds (model loading)
- **Warm Invocation**: ~2-5 seconds
- **Optimization**: Use provisioned concurrency for production

### Enable Provisioned Concurrency

```bash
aws lambda put-provisioned-concurrency-config \
  --function-name rti-voice-service \
  --provisioned-concurrent-executions 1 \
  --qualifier $LATEST \
  --region ap-south-1
```

## Monitoring

### CloudWatch Metrics

- Invocations
- Duration
- Errors
- Throttles

### CloudWatch Logs

```bash
aws logs tail /aws/lambda/rti-voice-service --follow --region ap-south-1
```

### X-Ray Tracing

Enabled by default for performance analysis.

## Troubleshooting

### Cold Start Too Slow

- Enable provisioned concurrency
- Reduce model size (use smaller Whisper variant)
- Optimize Docker image layers

### Out of Memory

- Increase Lambda memory (current: 10GB)
- Optimize model loading
- Use model quantization

### Transcription Accuracy Low

- Check audio quality (16kHz recommended)
- Verify language detection
- Try explicit language parameter

## Cost Optimization

- **Lambda**: ~$0.0000166667 per GB-second
- **ECR Storage**: ~$0.10 per GB/month
- **Provisioned Concurrency**: ~$0.0000041667 per GB-second

**Estimated cost for 1000 requests/month**: ~$5-10

## Next Steps

1. Add TTS functionality (Task 2.3)
2. Implement language switching (Task 3)
3. Add property-based tests (Task 2.2)
4. Optimize cold start time
