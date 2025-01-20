FROM python:3.13-slim
ARG VERSION=unknown

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
COPY . .

# Change ownership of the application directory
RUN chown -R appuser:appuser /app

# Python setup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VERSION=${VERSION}
ENV ENV=DEV

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Switch to the non-root user
USER appuser

EXPOSE 9000
CMD ["uvicorn", "app.main:app", "--workers", "6" , "--host", "0.0.0.0", "--port", "9000"]

# Install curl
USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl && apt-get clean

# Switch back to the non-root user
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --retries=5 \
  CMD curl --fail http://localhost:9000/openapi.json || exit 1
