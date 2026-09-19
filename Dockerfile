# Changed to 3.10-slim to fix the 404 apt errors
FROM python:3.10-slim

# Set working directory first
WORKDIR /app

# Combined all apt commands to fix duplicate installs, save space, and clear cache
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    ffmpeg \
    neofetch \
    software-properties-common && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir wheel && \
    pip3 install --no-cache-dir -U -r requirements.txt

# Copy the rest of the code
COPY . .

EXPOSE 8000

CMD flask run -h 0.0.0.0 -p 8000 & python3 -m devgagan

