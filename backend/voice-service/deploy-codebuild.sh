#!/bin/bash

# Deploy Voice Service using AWS CodeBuild (no local Docker needed)

set -e

echo "========================================="
echo "Voice Service - CodeBuild Deployment"
echo "========================================="

AWS_REGION="${AWS_REGION:-ap-south-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
PROJECT_NAME="rti-voice-service-build"

echo "AWS Region: $AWS_REGION"
echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "========================================="

# Create CodeBuild project if it doesn't exist
echo "Creating CodeBuild project..."
cat > /tmp/codebuild-project.json <<EOF
{
  "name": "$PROJECT_NAME",
  "source": {
    "type": "NO_SOURCE",
    "buildspec": "$(cat buildspec.yml | jq -Rs .)"
  },
  "artifacts": {
    "type": "NO_ARTIFACTS"
  },
  "environment": {
    "type": "LINUX_CONTAINER",
    "image": "aws/codebuild/standard:7.0",
    "computeType": "BUILD_GENERAL1_LARGE",
    "privilegedMode": true,
    "environmentVariables": [
      {
        "name": "AWS_DEFAULT_REGION",
        "value": "$AWS_REGION"
      },
      {
        "name": "AWS_ACCOUNT_ID",
        "value": "$AWS_ACCOUNT_ID"
      },
      {
        "name": "IMAGE_REPO_NAME",
        "value": "rti-voice-service"
      },
      {
        "name": "LAMBDA_FUNCTION_NAME",
        "value": "rti-voice-service"
      },
      {
        "name": "LAMBDA_ROLE_ARN",
        "value": "arn:aws:iam::$AWS_ACCOUNT_ID:role/rti-lambda-execution-role-dev"
      }
    ]
  },
  "serviceRole": "arn:aws:iam::$AWS_ACCOUNT_ID:role/codebuild-service-role"
}
EOF

aws codebuild create-project --cli-input-json file:///tmp/codebuild-project.json --region $AWS_REGION 2>/dev/null || \
  echo "CodeBuild project already exists"

# Upload source to S3
echo "Uploading source code..."
BUCKET_NAME="rti-codebuild-source-$AWS_ACCOUNT_ID"
aws s3 mb s3://$BUCKET_NAME --region $AWS_REGION 2>/dev/null || true

zip -r /tmp/voice-service.zip . -x "*.git*" "*.pyc" "__pycache__/*"
aws s3 cp /tmp/voice-service.zip s3://$BUCKET_NAME/voice-service.zip --region $AWS_REGION

# Start build
echo "Starting CodeBuild..."
BUILD_ID=$(aws codebuild start-build \
  --project-name $PROJECT_NAME \
  --source-type-override S3 \
  --source-location-override $BUCKET_NAME/voice-service.zip \
  --region $AWS_REGION \
  --query 'build.id' \
  --output text)

echo "Build started: $BUILD_ID"
echo "Monitor build: https://console.aws.amazon.com/codesuite/codebuild/projects/$PROJECT_NAME/build/$BUILD_ID"
echo ""
echo "Waiting for build to complete..."
aws codebuild wait build-complete --ids $BUILD_ID --region $AWS_REGION

echo "========================================="
echo "Deployment complete!"
echo "========================================="
