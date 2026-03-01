# Dockerfile for IndicWhisper Lambda Container
FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies for audio processing
RUN yum install -y \
    gcc \
    gcc-c++ \
    make \
    ffmpeg \
    libsndfile \
    && yum clean all

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (use pre-built wheels only to avoid GCC version issues)
RUN pip install --no-cache-dir --only-binary=:all: boto3 pydantic python-dotenv soundfile pydub joblib && \
    pip install --no-cache-dir numpy==1.24.3 scipy==1.11.4 scikit-learn==1.3.2 && \
    pip install --no-cache-dir torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir transformers==4.36.0 librosa==0.10.0

# Download and cache IndicWhisper model
RUN python -c "from transformers import WhisperProcessor, WhisperForConditionalGeneration; \
    model_name = 'vasista22/whisper-hindi-large-v2'; \
    processor = WhisperProcessor.from_pretrained(model_name); \
    model = WhisperForConditionalGeneration.from_pretrained(model_name); \
    print('IndicWhisper model cached successfully')"

# Copy shared modules (must be copied into voice-service directory first)
COPY shared ./shared

# Copy Lambda function code
COPY handler.py .
COPY transcribe.py .
COPY language_detector.py .

# Set the CMD to your handler
CMD [ "handler.lambda_handler" ]
