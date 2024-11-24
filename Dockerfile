FROM python:3.12-slim
ARG VERSION=unkown

WORKDIR /app
COPY . .

# Python setup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VERSION=${VERSION}
ENV ENV=DEV

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install 'uvicorn[standard]'

EXPOSE 9000
CMD ["uvicorn", "app.main:app", "--workers", "6" , "--host", "0.0.0.0", "--port", "9000"]

# Install curl
RUN apt-get update && apt-get install -y --no-install-recommends curl && apt-get clean

HEALTHCHECK --interval=30s --timeout=10s --retries=5 \
  CMD curl --fail http://localhost:9000/openapi.json || exit 1
