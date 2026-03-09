# RTI Voice Assistant - Updated Deployment Guide

This guide provides the most up-to-date instructions for deploying the RTI Voice Assistant backend and frontend to AWS. It incorporates all the fixes and best practices identified during the development process.

## Prerequisites

1.  **AWS Account** with appropriate permissions.
2.  **AWS CLI** installed and configured.
    ```bash
    aws configure
    ```
3.  **Node.js 18+** and npm (for frontend development).
4.  **Python 3.11+** (for backend development and Lambda layer creation).
5.  **Git** installed.
6.  **`zip` utility**: Ensure `zip` is available in your shell environment (e.g., Git Bash on Windows, or a Linux environment). If not, the script will provide instructions for manual zipping.
7.  **Environment Variables**: Ensure `GROQ_API_KEY` and `GEMINI_API_KEY` are set in your shell environment.

## Step 1: Deploy Backend Infrastructure and API

This step deploys the entire backend, including Lambda functions, API Gateway, DynamoDB tables, S3 buckets, and IAM roles, using CloudFormation.

1.  **Navigate to the `infrastructure/cloudformation` directory**:
    ```bash
    cd infrastructure/cloudformation
    ```

2.  **Make the deployment script executable**:
    ```bash
    chmod +x deploy.sh
    ```

3.  **Run the deployment script**:
    This script will:
    *   Create a Lambda layer with all Python dependencies.
    *   Create a deployment package for your backend application code.
    *   Upload both the layer and the application package to your specified S3 bucket.
    *   Deploy the main CloudFormation stack (`rti-voice-assistant`).
    *   Deploy the API routes CloudFormation stack (`rti-voice-assistant-api-routes`).
    *   Output the final API endpoint.

    You need to provide an `environment` (e.g., `dev`), an S3 `deployment-bucket-name` (where deployment artifacts will be stored), and a `deployment-bucket-key` (the filename for your application's zip package, e.g., `deployment_package.zip`).

    ```bash
    ./deploy.sh dev your-s3-deployment-bucket-name deployment_package.zip
    ```
    *Replace `your-s3-deployment-bucket-name` with an S3 bucket you own and have write access to. This bucket will be created if it doesn't exist.*

    **Important Notes during script execution:**
    *   If the `zip` command is not found, the script will pause and instruct you to manually create the zip files and upload them to S3. Follow the on-screen instructions carefully.
    *   If the CloudFormation stack gets stuck in a `UPDATE_FAILED` state (e.g., due to previous debugging attempts), you might need to delete the stack first:
        ```bash
        aws cloudformation delete-stack --stack-name rti-voice-assistant
        ```
        Wait for the deletion to complete before re-running the `./deploy.sh` script.

4.  **Verify Backend Deployment**:
    The script will output the API Endpoint. You can also check the status of your CloudFormation stacks in the AWS Console.
    *   `rti-voice-assistant` (main infrastructure)
    *   `rti-voice-assistant-api-routes` (API Gateway routes)

## Step 2: Configure Frontend API Endpoint

Now that your backend is deployed, you need to update your frontend application to point to the new API endpoint.

1.  **Update `.env.example`**:
    The `NEXT_PUBLIC_API_URL` in your `.env.example` file should be updated with the API Endpoint URL obtained from the backend deployment (output by the `deploy.sh` script).

    *Example `NEXT_PUBLIC_API_URL` entry in `.env.example`:*
    ```
    NEXT_PUBLIC_API_URL=api_endpoint # Deployed backend API endpoint
    ```

2.  **Update `.env` (if it exists)**:
    If you have a `.env` file in your project root, ensure its `NEXT_PUBLIC_API_URL` is also updated to the correct API endpoint. If you don't have a `.env` file, create one by copying `.env.example` and ensure `NEXT_PUBLIC_API_URL` is set.

3.  **Rename Frontend `lib` directory**:
    To avoid conflicts with Python `lib/` directories that are typically git-ignored, rename your frontend's `lib` directory.
    *   Navigate to `frontend/src/`.
    *   Rename the `lib` folder to `client-lib` (or a similar descriptive name).
        ```bash
        mv frontend/src/lib frontend/src/client-lib
        ```
    *   Update all import statements in your frontend code that refer to `@/lib/api` (or similar) to `@/client-lib/api`. You will need to search and replace these imports throughout your frontend codebase.

## Step 3: Deploy Frontend to AWS Amplify

AWS Amplify is recommended for deploying your Next.js frontend due to its ease of use and integrated CI/CD.

1.  **Commit your changes**:
    Ensure all changes (updated `.env.example`, `.env`, renamed `client-lib` folder, and updated import statements) are committed and pushed to your Git repository.

2.  **Access the AWS Amplify Console**:
    *   Go to the [AWS Amplify Console](https://console.aws.amazon.com/amplify/home).
    *   Click on "New app" → "Host web app".

3.  **Connect Your Repository**:
    *   Choose your Git provider (e.g., GitHub, GitLab, Bitbucket, AWS CodeCommit).
    *   Follow the authorization steps.
    *   Select your repository and the branch you want to deploy.
    *   Click "Next".

4.  **Configure Build Settings**:
    *   **App name**: Give your application a name (e.g., `rti-voice-assistant-frontend`).
    *   **App root / Base directory**: Set this to `frontend/`. This tells Amplify where your Next.js application's code is located within your monorepo.
    *   **Build settings**: Amplify usually auto-detects Next.js. Review the generated `amplify.yml` file. It should look similar to this:
        ```yaml
        version: 1
        frontend:
          phases:
            preBuild:
              commands:
                - npm ci
            build:
              commands:
                - npm run build
          artifacts:
            baseDirectory: .next
            files:
              - '**/*'
          cache:
            paths:
              - node_modules/**/*
        ```
        *Note: The `baseDirectory` here refers to the output of the `npm run build` command relative to the `App root` (`frontend/`).*
    *   **Environment variables**:
        *   Click on "Add environment variables".
        *   Add `NEXT_PUBLIC_API_URL` and paste the API endpoint: `api_end_point`.
        *   Add any other `NEXT_PUBLIC_` variables from your `.env` file that the frontend needs.
    *   Click "Next".

5.  **Review and Deploy**:
    *   Review all the settings.
    *   Click "Save and deploy".

6.  **Monitor Deployment**:
    *   Monitor the deployment progress in the Amplify Console.

7.  **Verify Your Deployed Frontend**:
    *   Once deployed, Amplify will provide a URL for your hosted frontend application. Open this URL in your browser to verify that your frontend is working and connecting to the backend API.

## Troubleshooting

*   **Lambda Layer Size**: If you encounter errors related to Lambda layer size, ensure `boto3` and `botocore` are removed from `backend/requirements.txt` as they are included in the Lambda runtime.
*   **CloudFormation Template Errors**: If you get `Template format error` messages, double-check all `Default` values for parameters are strings (e.g., `"24"` instead of `24`) and that numeric keys in YAML are quoted (e.g., `"200":`).
*   **Duplicate Export Names**: Ensure that CloudFormation output export names are unique across all your stacks.
*   **Reserved Lambda Environment Variables**: Do not set reserved Lambda environment variables like `AWS_REGION` manually.
*   **Incorrect Deployment Package Structure**: Ensure your `deployment_package.zip` contains the application files (e.g., `app.py`, `lambda_function.py`) at its root, not nested inside a `backend` folder.
*   **Frontend Module Not Found**: If frontend build fails with `Module not found`, ensure all necessary frontend code is committed to your Git repository and not ignored by `.gitignore`. If you rename a folder (e.g., `lib` to `client-lib`), update all import paths accordingly.
*   **Shell Quoting Issues**: When passing parameters to AWS CLI commands, especially those with special characters (like ARNs), always enclose the values in double quotes (e.g., `FastApiLambdaFunctionArn="arn:aws:lambda:..."`).

## Rollback

To delete the entire backend infrastructure deployed via CloudFormation:
```bash
aws cloudformation delete-stack --stack-name rti-voice-assistant
aws cloudformation delete-stack --stack-name rti-voice-assistant-api-routes
```
To delete the Amplify frontend application, use the AWS Amplify Console.

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