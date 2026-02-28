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

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download and cache IndicWhisper model
RUN python -c "from transformers import WhisperProcessor, WhisperForConditionalGeneration; \
    model_name = 'vasista22/whisper-hindi-large-v2'; \
    processor = WhisperProcessor.from_pretrained(model_name); \
    model = WhisperForConditionalGeneration.from_pretrained(model_name); \
    print('IndicWhisper model cached successfully')"

# Copy shared modules
COPY ../shared ./shared

# Copy Lambda function code
COPY handler.py .
COPY transcribe.py .
COPY language_detector.py .

# Set the CMD to your handler
CMD [ "handler.lambda_handler" ]
