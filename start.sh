#!/bin/bash
set -e

# Start bgutil-ytdlp-pot-provider HTTP server in background
# This generates PO tokens for YouTube to bypass bot checks
node /opt/bgutil-ytdlp-pot-provider/server/build/main.js &
PROVIDER_PID=$!

# Wait for provider server to be ready (max 15 seconds)
for i in $(seq 1 15); do
    if curl -sf http://127.0.0.1:4416 > /dev/null 2>&1; then
        echo "✅ YouTube PO token provider ready on port 4416"
        break
    fi
    echo "⏳ Waiting for PO token provider... ($i/15)"
    sleep 1
done

# Start the bot
python3 -m leechbot

# When bot exits, stop the provider server
kill $PROVIDER_PID 2>/dev/null || true
wait $PROVIDER_PID 2>/dev/null || true
