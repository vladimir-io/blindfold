
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	TRANSFORMERS_CACHE=/app/model_cache

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from transformers import AutoTokenizer, AutoModelForTokenClassification; \
	MODEL_NAME = 'openai/pii-1.5b'; \
	AutoTokenizer.from_pretrained(MODEL_NAME); \
	AutoModelForTokenClassification.from_pretrained(MODEL_NAME)"

COPY . .

RUN useradd -m blindfold && chown -R blindfold /app
USER blindfold

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
