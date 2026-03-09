#!/bin/bash

# RTI Voice Assistant - CloudFormation Deployment Script

set -e
set -x # Enable debugging output

# Disable Git Bash path conversion
export MSYS_NO_PATHCONV=1

# Configuration
STACK_NAME="rti-voice-assistant"
MAIN_TEMPLATE_FILE="main.yaml" # Renamed TEMPLATE_FILE for clarity
API_ROUTES_TEMPLATE_FILE="api-routes.yaml"
ENVIRONMENT="${1:-dev}"
REGION="${AWS_REGION:-ap-south-1}"
DEPLOYMENT_BUCKET_NAME="${2}" # Re-enabled for CloudFormation packaging
# LAYER_PACKAGE_KEY="lambda-layer.zip" # No longer needed for Docker deployment
API_ROOT_PATH="/${ENVIRONMENT}" # Set API root path based on environment

# Check for required parameters
if [ -z "$DEPLOYMENT_BUCKET_NAME" ]; then
    echo "Usage: $0 [environment] [deployment-bucket-name]"
    exit 1
fi

# Check for required environment variables
if [ -z "$GROQ_API_KEY" ] || [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: GROQ_API_KEY and GEMINI_API_KEY environment variables must be set."
    exit 1
fi

echo "========================================="
echo "RTI Voice Assistant - Infrastructure Deployment"
echo "========================================="
echo "Stack Name: $STACK_NAME"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "========================================="

# Docker Image Configuration
ECR_REPOSITORY_NAME="rti-voice-assistant-backend-${ENVIRONMENT}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_FULL_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}"
IMAGE_TAG="latest"

echo "========================================="
echo "Building and Pushing Docker Image"
echo "========================================="

# Create ECR repository if it doesn't exist
echo "Checking for ECR repository: $ECR_REPOSITORY_NAME"
aws ecr describe-repositories --repository-names "$ECR_REPOSITORY_NAME" --region "$REGION" > /dev/null 2>&1 || \
aws ecr create-repository \
    --repository-name "$ECR_REPOSITORY_NAME" \
    --image-tag-mutability MUTABLE \
    --image-scanning-configuration scanOnPush=true \
    --region "$REGION"

# Authenticate Docker to ECR
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

# Build the Docker image
# Disable BuildKit to avoid OCI index manifests
export DOCKER_BUILDKIT=0

# Build the Docker image (single architecture)
docker build --platform linux/amd64 \
  -t "$ECR_REPOSITORY_NAME:$IMAGE_TAG" \
  ../../backend/

# Tag for ECR
docker tag "$ECR_REPOSITORY_NAME:$IMAGE_TAG" \
  "$ECR_FULL_URI:$IMAGE_TAG"

# Push to ECR
docker push "$ECR_FULL_URI:$IMAGE_TAG"

echo "Docker image pushed to ECR: $ECR_FULL_URI:$IMAGE_TAG"
echo "========================================="

# Package the CloudFormation templates
echo "Packaging CloudFormation templates..."
PACKAGED_TEMPLATE_FILE="packaged-main.yaml"
aws cloudformation package \
    --template-file "$MAIN_TEMPLATE_FILE" \
    --s3-bucket "$DEPLOYMENT_BUCKET_NAME" \
    --s3-prefix "cloudformation-templates" \
    --output-template-file "$PACKAGED_TEMPLATE_FILE" \
    --region "$REGION"

# Validate template
echo "Validating CloudFormation template..."
aws cloudformation validate-template \
    --template-body file://$PACKAGED_TEMPLATE_FILE \
    --region $REGION

# Check if stack exists and its status
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].StackStatus" --output text 2>/dev/null || echo "DOES_NOT_EXIST")

if [ "$STACK_STATUS" == "ROLLBACK_COMPLETE" ]; then
    echo "Stack is in ROLLBACK_COMPLETE state. Deleting stack before re-creation..."
    aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION
    echo "Waiting for stack deletion to complete..."
    aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $REGION
    STACK_STATUS="DOES_NOT_EXIST" # Reset status so it proceeds with creation
fi

if [ "$STACK_STATUS" != "DOES_NOT_EXIST" ]; then
    echo "Stack exists. Updating..."
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://$PACKAGED_TEMPLATE_FILE \
        --parameters \
            ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
            ParameterKey=GroqApiKey,ParameterValue=$GROQ_API_KEY \
            ParameterKey=GeminiApiKey,ParameterValue=$GEMINI_API_KEY \
            ParameterKey=ApiRootPath,ParameterValue="${API_ROOT_PATH}" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
    
    echo "Waiting for stack update to complete..."
    aws cloudformation wait stack-update-complete \
        --stack-name $STACK_NAME \
        --region $REGION
else
    echo "Stack does not exist or was deleted. Creating..."
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://$PACKAGED_TEMPLATE_FILE \
        --parameters \
            ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
            ParameterKey=GroqApiKey,ParameterValue=$GROQ_API_KEY \
            ParameterKey=GeminiApiKey,ParameterValue=$GEMINI_API_KEY \
            ParameterKey=ApiRootPath,ParameterValue="${API_ROOT_PATH}" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION \
        --tags Key=Environment,Value=$ENVIRONMENT Key=Application,Value=RTI-Voice-Assistant
    
    echo "Waiting for stack creation to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name $STACK_NAME \
        --region $REGION
fi

echo "========================================="
echo "Main stack deployment complete!"
echo "========================================="

# Get outputs from the main stack
echo "Getting outputs from main stack..."
HttpApiId=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='HttpApiId'].OutputValue" --output text)
FastApiLambdaFunctionArn=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='FastApiLambdaFunctionArn'].OutputValue" --output text)

# Deploy the API routes stack
API_ROUTES_STACK_NAME="${STACK_NAME}-api-routes"
API_ROUTES_TEMPLATE_FILE="api-routes.yaml"

echo "========================================="
echo "Deploying API routes stack..."
echo "API Routes Stack Name: $API_ROUTES_STACK_NAME"
echo "========================================="

aws cloudformation deploy \
    --template-file "$API_ROUTES_TEMPLATE_FILE" \
    --stack-name "$API_ROUTES_STACK_NAME" \
    --parameter-overrides \
        Environment="$ENVIRONMENT" \
        HttpApiId="$HttpApiId" \
        FastApiLambdaFunctionArn="$FastApiLambdaFunctionArn" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$REGION"

echo "========================================="
echo "Deployment complete!"
echo "========================================="

# Get stack outputs
echo "Stack Outputs:"
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table

    echo ""
    echo "API Endpoint: $(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey=="HttpApiUrl"].OutputValue' --output text)"
    echo ""
    echo "Next steps:"
    echo "1. Update the NEXT_PUBLIC_API_URL in your frontend's .env file with the API Endpoint above."
    echo "2. Deploy your frontend application to AWS Amplify."
