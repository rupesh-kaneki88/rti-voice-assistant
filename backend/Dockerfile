# 1. Use a slim and secure base image
FROM python:3.11-slim

# 2. Set the working directory
WORKDIR /app

# 3. Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 5. Copy the rest of your application code
COPY . .

# 6. Define the command to run your application
#    - Uses "python -m uvicorn" which is more reliable in containers.
#    - App Runner will set the PORT environment variable, which defaults to 8080.
#      This command will use that port, or fall back to 8000 if it's not set.
CMD python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
