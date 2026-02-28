#!/bin/bash

# RTI Voice Assistant - CloudFormation Deployment Script

set -e

# Configuration
STACK_NAME="rti-voice-assistant"
TEMPLATE_FILE="main.yaml"
ENVIRONMENT="${1:-dev}"
REGION="${AWS_REGION:-ap-south-1}"

echo "========================================="
echo "RTI Voice Assistant - Infrastructure Deployment"
echo "========================================="
echo "Stack Name: $STACK_NAME"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "========================================="

# Validate template
echo "Validating CloudFormation template..."
aws cloudformation validate-template \
    --template-body file://$TEMPLATE_FILE \
    --region $REGION

# Check if stack exists
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION >/dev/null 2>&1; then
    echo "Stack exists. Updating..."
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --parameters ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
    
    echo "Waiting for stack update to complete..."
    aws cloudformation wait stack-update-complete \
        --stack-name $STACK_NAME \
        --region $REGION
else
    echo "Stack does not exist. Creating..."
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --parameters ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION \
        --tags Key=Environment,Value=$ENVIRONMENT Key=Application,Value=RTI-Voice-Assistant
    
    echo "Waiting for stack creation to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name $STACK_NAME \
        --region $REGION
fi

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
echo "Next steps:"
echo "1. Update .env file with the output values"
echo "2. Deploy Lambda functions: cd ../backend && ./deploy.sh"
echo "3. Deploy frontend: cd ../frontend && npm run deploy"
