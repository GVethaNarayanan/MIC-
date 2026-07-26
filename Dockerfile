# Use official python slim image
FROM python:3.10-slim

# Install system dependencies (ffmpeg is required for Whisper!)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up user with UID 1000 (recommended by Hugging Face)
RUN useradd -m -u 1000 user
WORKDIR /app

# Copy requirements and install dependencies
COPY --chown=user requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY --chown=user . /app/

# Create folders for history and cached models
RUN mkdir -p /app/data /app/static/audio && chown -R user:user /app

# Switch to the non-root user
USER user

# Set env variables
ENV PORT=7860
ENV HOME=/home/user
ENV TRANSFORMERS_CACHE=/home/user/.cache/huggingface

# Pre-download the Whisper base model and NLLB model/tokenizer to ensure instant startup
RUN python -c "import whisper; whisper.load_model('base')"
RUN python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; AutoTokenizer.from_pretrained('facebook/nllb-200-distilled-600M'); AutoModelForSeq2SeqLM.from_pretrained('facebook/nllb-200-distilled-600M')"

# Expose port 7860
EXPOSE 7860

# Run the app
CMD ["python", "app.py"]
