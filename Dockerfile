# Single-stage build
FROM node:24-slim

# Install Python
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    build-essential
# Set working directory
WORKDIR /app
RUN python3 -m venv venv

# Copy everything
COPY . .

# Build frontend
RUN cd frontend && npm install && npm run build

# Create static directory and copy build output
RUN mkdir -p /app/static && \
    cp -r frontend/build/* /app/static/ || cp -r frontend/dist/* /app/static/

# Install Python dependencies
COPY api/requirements.txt /app/api/requirements.txt

RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install -r /app/api/requirements.txt

# Set the working directory to the backend
WORKDIR /app/api

# Set environment variables (optional, if needed by app)
ENV PATH="/app/venv/bin:$PATH"

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "entrypoint:app"]