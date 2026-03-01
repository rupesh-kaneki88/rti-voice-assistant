#!/bin/bash

# Voice Service Lambda Deployment Script

set -e

echo "========================================="
echo "Voice Service Lambda - Deployment"
echo "========================================="

# Configuration
AWS_REGION="${AWS_REGION:-ap-south-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="rti-voice-service"
IMAGE_TAG="${1:-latest}"
FUNCTION_NAME="rti-voice-service"
LAMBDA_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/rti-lambda-execution-role-dev"

echo "AWS Region: $AWS_REGION"
echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "ECR Repository: $ECR_REPOSITORY"
echo "Image Tag: $IMAGE_TAG"
echo "========================================="

# Copy shared modules into build context
echo "Copying shared modules..."
rm -rf shared
cp -r ../shared ./shared

# Create ECR repository if it doesn't exist
echo "Creating ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null || \
    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

# Get ECR login token
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build Docker image
echo "Building Docker image..."
docker build -t $ECR_REPOSITORY:$IMAGE_TAG .

# Tag image for ECR
echo "Tagging image..."
docker tag $ECR_REPOSITORY:$IMAGE_TAG ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG

# Push image to ECR
echo "Pushing image to ECR..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG

# Create or update Lambda function
echo "Checking if Lambda function exists..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION 2>/dev/null; then
    echo "Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --image-uri ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG \
        --region $AWS_REGION
else
    echo "Creating new Lambda function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --package-type Image \
        --code ImageUri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG \
        --role $LAMBDA_ROLE_ARN \
        --timeout 900 \
        --memory-size 10240 \
        --region $AWS_REGION \
        --environment Variables="{LOG_LEVEL=INFO,AWS_REGION=$AWS_REGION}" \
        --description "RTI Voice Service - Speech-to-Text with IndicWhisper"
fi

# Wait for function to be active
echo "Waiting for Lambda function to be active..."
aws lambda wait function-active --function-name $FUNCTION_NAME --region $AWS_REGION

# Enable X-Ray tracing
echo "Enabling X-Ray tracing..."
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --tracing-config Mode=Active \
    --region $AWS_REGION

echo "========================================="
echo "Deployment complete!"
echo "========================================="
echo "Function ARN:"
aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION --query 'Configuration.FunctionArn' --output text

echo ""
echo "Test the function:"
echo "aws lambda invoke --function-name $FUNCTION_NAME --payload file://test_event.json response.json --region $AWS_REGION"
