#!/bin/bash
# start.sh - Production startup script for the Django application

set -e  # Exit on any error

PORT=${PORT:-8000}  # Gets PORT from env or uses 8000 as fallback

echo "Executing migrations..."
python manage.py migrate

# Collect static files from all applications into the STATIC_ROOT directory
echo "Executing collectstatic..."
# Run collectstatic without asking for confirmation (--no-input flag)
python manage.py collectstatic --no-input

# Start the Django application using Gunicorn WSGI server
echo "Starting Gunicorn with Django"
# Run Gunicorn with the following configuration:
# --capture-output: Capture and redirect stdout/stderr to logging system
# --bind :$PORT: Bind the server to the previously defined PORT on all interfaces
# --workers 3: Use 3 worker processes to handle requests
# cdc.wsgi:application: Path to the WSGI application object
gunicorn --capture-output --bind :$PORT --workers 3 cdc.wsgi:application