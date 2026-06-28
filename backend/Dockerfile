FROM python:3.11-slim

# System deps for PyMuPDF and FAISS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgomp1 libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data dirs
RUN mkdir -p data/raw/pdfs data/processed data/vectorstore

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
