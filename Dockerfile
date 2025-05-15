# Single-stage build
FROM node:24-slim

# Install Python
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    build-essential
# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Build frontend
RUN cd frontend && npm install && npm run build

# Create static directory and copy build output
RUN mkdir -p /app/api/static && \
    cp -r frontend/build/* /app/api/static/ || cp -r frontend/dist/* /app/api/static/


# Create and activate virtual environment
RUN python3.11 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/backend/requirements.txt


# Set the working directory to the backend
WORKDIR /app/backend

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:3000","--timeout", "180", "entrypoint:app"]