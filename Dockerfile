# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime (minimal image)
FROM python:3.11-slim

# Set UTC timezone (required!)
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install only cron (tiny footprint)
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code and keys
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY cron/ ./cron/
COPY student_private.pem student_public.pem instructor_public.pem ./

# Install cron job with correct permissions
RUN chmod 0644 /app/cron/2fa-cron
RUN crontab /app/cron/2fa-cron

# Create persistent directories
RUN mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080

# Start cron + FastAPI
CMD cron && uvicorn app.main:app --host 0.0.0.0 --port 8080