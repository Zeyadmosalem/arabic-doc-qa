FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user

ENV PATH="/home/user/.local/bin:$PATH" \
    HF_HOME=/home/user/.cache/huggingface \
    PYTHONUNBUFFERED=1

WORKDIR /app

# CPU-only torch from PyTorch's own index. The default PyPI wheel bundles CUDA
# and is ~2.5 GB, which a CPU service has no use for — and on Cloud Run image
# size is paid for in cold-start time.
RUN pip install --no-cache-dir --user \
    torch --index-url https://download.pytorch.org/whl/cpu

COPY --chown=user pyproject.toml ./
COPY --chown=user app ./app
RUN pip install --no-cache-dir --user .

# Bake the embedding model into the image. Downloading 1.1 GB on first request
# would blow past Cloud Run's startup probe and make every cold start look dead.
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('intfloat/multilingual-e5-base')"

# Cloud Run injects PORT and expects the container to honour it. Shell form so
# the variable is expanded; the default keeps `docker run` working locally.
EXPOSE 8080
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
