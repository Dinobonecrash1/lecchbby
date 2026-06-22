FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg aria2 p7zip-full unrar megatools git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x (required for bgutil-ytdlp-pot-provider server)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install bgutil-ytdlp-pot-provider HTTP server
# This generates PO tokens for YouTube to bypass "Sign in to confirm you're not a bot"
RUN git clone --single-branch --branch 1.3.1 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /opt/bgutil-ytdlp-pot-provider && \
    cd /opt/bgutil-ytdlp-pot-provider/server && npm ci && npx tsc

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY . .

# Start provider server in background, then bot
CMD ["/bin/bash", "-c", "node /opt/bgutil-ytdlp-pot-provider/server/build/main.js & python3 -m leechbot"]
