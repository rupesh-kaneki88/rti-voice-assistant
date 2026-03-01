#!/bin/bash

# Simplified deployment script for Voice Service Lambda (without Docker)
# This version uses a simple ZIP deployment for infrastructure testing

set -e

# Configuration
AWS_REGION="${AWS_REGION:-ap-south-1}"
FUNCTION_NAME="rti-voice-service"
LAMBDA_ROLE_NAME="RTIVoiceServiceRole"

echo "========================================="
echo "Voice Service Lambda - Simple Deployment"
echo "========================================="
echo "AWS Region: $AWS_REGION"
echo "Function Name: $FUNCTION_NAME"
echo "========================================="

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"

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

# Create deployment package
echo ""
echo "Creating deployment package..."
rm -rf lambda-package
mkdir -p lambda-package

# Copy handler
cp handler_simple.py lambda-package/

# Copy shared modules
cp -r ../shared lambda-package/

# Install dependencies
pip install -r requirements-simple.txt -t lambda-package/

# Create ZIP
cd lambda-package
zip -r ../voice-service-simple.zip . > /dev/null
cd ..

echo "Deployment package created: voice-service-simple.zip"

# Deploy Lambda function
echo ""
echo "Deploying Lambda function..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION 2>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://voice-service-simple.zip \
        --region $AWS_REGION
    
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --handler handler_simple.lambda_handler \
        --runtime python3.11 \
        --timeout 30 \
        --memory-size 512 \
        --region $AWS_REGION
else
    echo "Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $LAMBDA_ROLE_ARN \
        --handler handler_simple.lambda_handler \
        --zip-file fileb://voice-service-simple.zip \
        --timeout 30 \
        --memory-size 512 \
        --region $AWS_REGION
fi

# Clean up
echo ""
echo "Cleaning up..."
rm -rf lambda-package voice-service-simple.zip

echo ""
echo "========================================="
echo "Deployment complete!"
echo "========================================="
echo "Function Name: $FUNCTION_NAME"
echo "Region: $AWS_REGION"
echo "Mode: SIMPLE (Mock responses)"
echo ""
echo "Test the function with:"
echo "aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"body\":{\"audio\":\"dGVzdA==\",\"language\":\"hi\"}}' /tmp/response.json --region $AWS_REGION"
echo "========================================="
