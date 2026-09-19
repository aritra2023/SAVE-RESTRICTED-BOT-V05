FROM python:3.10-slim

WORKDIR /app

# Removed neofetch and software-properties-common
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --no-cache-dir wheel && \
    pip3 install --no-cache-dir -U -r requirements.txt

COPY . .

EXPOSE 8000

CMD flask run -h 0.0.0.0 -p 8000 & python3 -m devgagan
