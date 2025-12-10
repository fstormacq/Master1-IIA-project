#!/bin/bash
# Script to start the Raspberry Pi system with monitor

# Start main.py in background
echo "🚀 Starting main.py..."
uv run main.py "$@" &
MAIN_PID=$!

# Wait a bit for initialization
sleep 2

# Start monitor in foreground
echo "📊 Starting monitor..."
uv run monitor_serial.py

# When monitor stops (Ctrl+C), kill main.py
echo "🛑 Stopping main.py..."
kill $MAIN_PID 2>/dev/null
wait $MAIN_PID 2>/dev/null

echo "✅ All processes stopped"