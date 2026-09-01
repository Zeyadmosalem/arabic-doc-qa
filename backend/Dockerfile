FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user

ENV PATH="/home/user/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --chown=user pyproject.toml ./
COPY --chown=user app ./app
RUN pip install --no-cache-dir --user .

# Hosts inject PORT and expect the container to honour it. Shell form so the
# variable is expanded; the default keeps `docker run` working locally.
EXPOSE 8080
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
