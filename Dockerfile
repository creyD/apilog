FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip  wheel --no-cache-dir --wheel-dir=/build/wheels \
    -r requirements.txt \

FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y curl git

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/*

# Remove the wheels directory after installation to save space
RUN rm -rf /wheels
# Python setup
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ARG VERSION=unknown
ENV VERSION=${VERSION}

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "6" , "-b", "0.0.0.0:9000","app.main:app"]
EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=10s --retries=5 \
  CMD curl --fail http://localhost:9000/openapi.json || exit 1
