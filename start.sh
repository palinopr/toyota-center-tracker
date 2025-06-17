#!/bin/bash
# Start script for Railway
echo "Starting Toyota Center Tracker..."
echo "PORT: $PORT"
echo "Python version:"
python --version
echo "Current directory:"
pwd
echo "Files in directory:"
ls -la
echo "Starting app..."
exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}