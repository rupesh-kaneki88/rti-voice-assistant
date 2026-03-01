#!/bin/bash

# Simplified Docker deployment script for Voice Service Lambda
# This version uses minimal dependencies for infrastructure testing

set -e

# Configuration
AWS_REGION="${AWS_REGION:-ap-south-1}"
ECR_REPO_NAME="rti-voice-service-simple"
FUNCTION_NAME="rti-voice-service"
IMAGE_TAG="${1:-latest}"
LAMBDA_ROLE_NAME="RTIVoiceServiceRole"

echo "========================================="
echo "Voice Service Lambda - Simple Docker Deployment"
echo "========================================="
echo "AWS Region: $AWS_REGION"
echo "ECR Repository: $ECR_REPO_NAME"
echo "Image Tag: $IMAGE_TAG"
echo "========================================="

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"

# Create ECR repository if it doesn't exist
echo ""
echo "Creating ECR repository..."
aws ecr create-repository \
    --repository-name $ECR_REPO_NAME \
    --region $AWS_REGION \
    2>/dev/null || echo "Repository already exists"

# Login to ECR
echo ""
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build Docker image
echo ""
echo "Building Docker image..."
docker build -f Dockerfile.simple -t ${ECR_REPO_NAME}:${IMAGE_TAG} ../

# Tag image for ECR
echo ""
echo "Tagging image..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}

# Push to ECR
echo ""
echo "Pushing image to ECR..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}

# Create IAM role if it doesn't exist
echo ""
echo "Checking IAM role..."
if ! aws iam get-role --role-name $LAMBDA_ROLE_NAME --region $AWS_REGION 2>/dev/null; then
    echo "Creating IAM role..."
    
    # Create trust policy in current directory
    cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
    
    aws iam create-role \
        --role-name $LAMBDA_ROLE_NAME \
        --assume-role-policy-document file://trust-policy.json \
        --region $AWS_REGION
    
    # Attach basic Lambda execution policy
    aws iam attach-role-policy \
        --role-name $LAMBDA_ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
        --region $AWS_REGION
    
    echo "Waiting for IAM role to propagate..."
    sleep 10
    
    # Clean up
    rm -f trust-policy.json
else
    echo "IAM role already exists"
fi

LAMBDA_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${LAMBDA_ROLE_NAME}"
echo "Lambda Role ARN: $LAMBDA_ROLE_ARN"

# Deploy or update Lambda function
echo ""
echo "Deploying Lambda function..."
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}"

if aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION 2>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --image-uri $IMAGE_URI \
        --region $AWS_REGION
    
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout 30 \
        --memory-size 512 \
        --region $AWS_REGION
else
    echo "Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --package-type Image \
        --code ImageUri=$IMAGE_URI \
        --role $LAMBDA_ROLE_ARN \
        --timeout 30 \
        --memory-size 512 \
        --region $AWS_REGION
fi

echo ""
echo "========================================="
echo "Deployment complete!"
echo "========================================="
echo "Function Name: $FUNCTION_NAME"
echo "Image URI: $IMAGE_URI"
echo "Region: $AWS_REGION"
echo "Mode: SIMPLE (Mock responses)"
echo ""
echo "Test the function with:"
echo "aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"body\":{\"audio\":\"dGVzdA==\",\"language\":\"hi\"}}' /tmp/response.json --region $AWS_REGION"
echo "========================================="
