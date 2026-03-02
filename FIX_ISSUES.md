# Fixing Current Issues

## Issue 1: AWS Payment Method (URGENT)

**Error**: `INVALID_PAYMENT_INSTRUMENT: A valid payment instrument must be provided`

**Solution**:
1. Go to: https://console.aws.amazon.com/billing/home#/paymentmethods
2. Click "Add payment method"
3. Add a **credit/debit card** (Visa/Mastercard/RuPay)
   - UPI does NOT work for AWS Bedrock
   - You need an international card or Indian debit card
4. Wait 2-3 minutes after adding
5. Try again

**Alternative if you don't have a card**:
- Ask a friend/family member to add their card temporarily
- Use a virtual card from apps like Paytm, PhonePe (if they support international transactions)
- For hackathon: Consider using the rule-based fallback (see below)

---

## Issue 2: DynamoDB Schema Mismatch

**Error**: `Missing the key sessionId in the item`

**Problem**: The DynamoDB table might have been created with wrong key name.

**Solution - Check and Recreate Table**:

```bash
cd backend

# Check current table schema
python check_dynamodb.py

# If it shows wrong key name, delete and recreate:
python -c "import boto3; boto3.client('dynamodb', region_name='ap-south-1').delete_table(TableName='rti-sessions-dev')"

# Wait 30 seconds, then recreate:
python setup_aws.py
```

**Quick Fix - Use Memory Storage**:

If DynamoDB keeps failing, use in-memory storage for testing:

In `backend/.env`:
```bash
USE_MOCK_SERVICES=true
```

This will store sessions in memory (lost on restart, but works for testing).

---

## Issue 3: Conversation Not Persisting

**Current Status**: Conversations ARE being stored, but there are two issues:
1. DynamoDB schema error prevents saving
2. No Redis needed - we're using DynamoDB

**What's Working**:
- ✅ Conversation history is tracked in session
- ✅ Form updates are extracted
- ✅ Agent responds contextually

**What's Not Working**:
- ❌ DynamoDB save fails due to schema
- ❌ Bedrock fails due to payment

**Fix**: Resolve issues 1 and 2 above.

---

## Testing Without Bedrock (Temporary)

If you can't add a payment method right now, the system will use rule-based fallback:

**What Works**:
- ✅ Basic conversation flow
- ✅ Form field extraction
- ✅ Step-by-step guidance
- ✅ Multilingual responses

**What's Limited**:
- ❌ Less natural language understanding
- ❌ No complex query handling
- ❌ Fixed response templates

**To Test**:
```bash
cd backend
python test_conversation.py
```

You should see rule-based responses instead of Bedrock errors.

---

## Quick Diagnostic Commands

### Check DynamoDB Table
```bash
cd backend
python check_dynamodb.py
```

### Check AWS Credentials
```bash
aws sts get-caller-identity
```

### Check Bedrock Access
```bash
aws bedrock list-foundation-models --region ap-south-1 --query "modelSummaries[?contains(modelId, 'claude')]"
```

### Check Payment Method
```bash
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics BlendedCost
```

---

## Priority Order

1. **Add payment method** (5 minutes)
   - This unblocks Bedrock
   - Most important for natural conversation

2. **Fix DynamoDB schema** (2 minutes)
   - Run check_dynamodb.py
   - Delete and recreate if needed

3. **Test conversation** (1 minute)
   - Run test_conversation.py
   - Should work end-to-end

---

## Expected Behavior After Fixes

```
1. Getting initial greeting...
Agent: Hello! I'm your RTI assistant...

2. User: I want to know about government spending on education
Agent: Great! I understand you want information about government spending on education. Which government department should I address this to?

3. User: Ministry of Education
Agent: Perfect! Now I need your name for the application.

4. User: My name is Rajesh Kumar
Agent: Thank you, Rajesh! What is your address?

... and so on
```

---

## Still Having Issues?

### DynamoDB Keeps Failing
Set `USE_MOCK_SERVICES=true` in `.env` - uses memory storage

### Bedrock Keeps Failing
The rule-based fallback will work automatically

### Want to Skip AWS Entirely
Set in `.env`:
```bash
USE_MOCK_SERVICES=true
```

Everything will work locally without AWS (but no persistence across restarts).

---

## For Hackathon Demo

If you can't fix AWS issues in time:

1. Use `USE_MOCK_SERVICES=true`
2. Demo will work perfectly for single session
3. Just restart backend between demos
4. Mention "Production version uses AWS DynamoDB and Bedrock"

The conversation logic is solid - it's just the AWS integration that needs the payment method!
