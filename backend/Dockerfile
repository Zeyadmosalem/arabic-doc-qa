FROM python:3.11-slim

# Hugging Face Spaces runs the container as uid 1000.
RUN useradd -m -u 1000 user
USER user

ENV PATH="/home/user/.local/bin:$PATH" \
    HF_HOME=/home/user/.cache/huggingface \
    PYTHONUNBUFFERED=1

WORKDIR /app

# CPU-only torch first, from PyTorch's own index. The default PyPI wheel bundles
# CUDA and is ~2.5 GB, which this image has no use for.
RUN pip install --no-cache-dir --user \
    torch --index-url https://download.pytorch.org/whl/cpu

COPY --chown=user pyproject.toml ./
COPY --chown=user app ./app
RUN pip install --no-cache-dir --user .

# Bake the embedding model into the image. Downloading 1.1 GB on first request
# would make every cold start look like a hang.
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('intfloat/multilingual-e5-base')"

EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
