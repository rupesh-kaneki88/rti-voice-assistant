"""
Setup script to create AWS resources for RTI Voice Assistant
Run this once to set up DynamoDB tables and S3 buckets
"""
import boto3
import sys
from botocore.exceptions import ClientError

# Configuration
AWS_REGION = 'ap-south-1'
DYNAMODB_SESSIONS_TABLE = 'rti-sessions-dev'
S3_DOCUMENTS_BUCKET = 'rti-documents-dev-' + boto3.client('sts').get_caller_identity()['Account']
S3_AUDIO_BUCKET = 'rti-audio-dev-' + boto3.client('sts').get_caller_identity()['Account']


def create_dynamodb_table():
    """Create DynamoDB table for sessions"""
    try:
        dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
        
        print(f"\nCreating DynamoDB table: {DYNAMODB_SESSIONS_TABLE}")
        
        dynamodb.create_table(
            TableName=DYNAMODB_SESSIONS_TABLE,
            KeySchema=[
                {'AttributeName': 'session_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'session_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand pricing
            Tags=[
                {'Key': 'Project', 'Value': 'RTI-Voice-Assistant'},
                {'Key': 'Environment', 'Value': 'dev'}
            ]
        )
        
        # Wait for table to be created
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=DYNAMODB_SESSIONS_TABLE)
        
        # Enable TTL
        dynamodb.update_time_to_live(
            TableName=DYNAMODB_SESSIONS_TABLE,
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': 'ttl'
            }
        )
        
        print(f"✓ DynamoDB table created: {DYNAMODB_SESSIONS_TABLE}")
        print(f"  - TTL enabled (24 hours)")
        print(f"  - Billing: Pay per request")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"✓ DynamoDB table already exists: {DYNAMODB_SESSIONS_TABLE}")
        else:
            print(f"✗ Error creating DynamoDB table: {e}")
            raise


def create_s3_buckets():
    """Create S3 buckets for documents and audio"""
    s3 = boto3.client('s3', region_name=AWS_REGION)
    
    buckets = [
        (S3_DOCUMENTS_BUCKET, 'RTI documents'),
        (S3_AUDIO_BUCKET, 'Audio files')
    ]
    
    for bucket_name, description in buckets:
        try:
            print(f"\nCreating S3 bucket: {bucket_name} ({description})")
            
            # Create bucket
            if AWS_REGION == 'us-east-1':
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                )
            
            # Enable versioning
            s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Set lifecycle policy (delete after 24 hours)
            s3.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration={
                    'Rules': [
                        {
                            'ID': 'DeleteAfter24Hours',
                            'Status': 'Enabled',
                            'Filter': {'Prefix': ''},
                            'Expiration': {'Days': 1},
                            'NoncurrentVersionExpiration': {'NoncurrentDays': 1}
                        }
                    ]
                }
            )
            
            # Enable encryption
            s3.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            )
            
            print(f"✓ S3 bucket created: {bucket_name}")
            print(f"  - Versioning: Enabled")
            print(f"  - Lifecycle: Delete after 24 hours")
            print(f"  - Encryption: AES256")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print(f"✓ S3 bucket already exists: {bucket_name}")
            else:
                print(f"✗ Error creating S3 bucket: {e}")
                raise


def update_env_file():
    """Update .env file with AWS resource names"""
    try:
        print("\nUpdating .env file...")
        
        account_id = boto3.client('sts').get_caller_identity()['Account']
        
        env_content = f"""# AWS Configuration
AWS_REGION={AWS_REGION}
AWS_ACCOUNT_ID={account_id}

# DynamoDB Tables
DYNAMODB_SESSIONS_TABLE={DYNAMODB_SESSIONS_TABLE}

# S3 Buckets
S3_DOCUMENTS_BUCKET={S3_DOCUMENTS_BUCKET}
S3_AUDIO_BUCKET={S3_AUDIO_BUCKET}

# LLM Providers (Groq/Gemini) - Add your keys here
GROQ_API_KEY=
GEMINI_API_KEY=

# AWS Polly
POLLY_VOICE_HINDI=Aditi
POLLY_VOICE_ENGLISH=Joanna
POLLY_OUTPUT_FORMAT=mp3

# Session Configuration
SESSION_TTL_HOURS=24

# Logging
LOG_LEVEL=INFO

# Use real AWS services (set to true for mock services)
USE_MOCK_SERVICES=false
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✓ .env file updated")
        
    except Exception as e:
        print(f"✗ Error updating .env file: {e}")


def main():
    """Main setup function"""
    print("=" * 60)
    print("RTI Voice Assistant - AWS Setup")
    print("=" * 60)
    
    try:
        # Check AWS credentials
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"\nAWS Account: {identity['Account']}")
        print(f"AWS Region: {AWS_REGION}")
        
        # Create resources
        create_dynamodb_table()
        create_s3_buckets()
        update_env_file()
        
        print("\n" + "=" * 60)
        print("✓ AWS Setup Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Add your GROQ_API_KEY and/or GEMINI_API_KEY to the .env file")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Start the server: uvicorn app:app --reload")
        print("\nEstimated costs with $100 credits:")
        print("  - DynamoDB: ~$0.01/day (pay per request)")
        print("  - S3: ~$0.01/day (with 24h lifecycle)")
        print("  - Transcribe: ~$0.024/minute")
        print("  - Polly: ~$0.004/1000 chars")
        print("  - Groq/Gemini: Check their respective pricing pages.")
        print("\nTotal: Should last a long time with moderate usage!")
        
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
