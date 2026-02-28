#!/bin/bash

# RTI Voice Assistant - Lambda Deployment Script

set -e

echo "========================================="
echo "RTI Voice Assistant - Lambda Deployment"
echo "========================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS CLI is not configured. Please run 'aws configure'"
    exit 1
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt -t ./package

# Copy shared modules
echo "Copying shared modules..."
cp -r shared ./package/

# Package Lambda functions (placeholder - will be implemented per service)
echo "Lambda functions will be packaged individually per service"
echo "See individual service directories for deployment scripts"

echo "========================================="
echo "Deployment preparation complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Deploy individual Lambda functions from their service directories"
echo "2. Update API Gateway with Lambda integrations"
echo "3. Test endpoints using Postman or curl"
