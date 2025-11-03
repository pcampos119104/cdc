#!/usr/bin/env xonsh
# start.xsh - Production startup script for the Django application

# Import necessary Python modules
import os          # For accessing environment variables and OS functionality

$RAISE_SUBPROC_ERROR = True  # Raises an exception if a subprocess returns non-zero exit code
$XONSH_TRACEBACK_LOGFILE = '/tmp/xonsh_traceback.log'  # Logs traceback info to this file for debugging

$PORT = os.getenv('PORT', '8000')  # Gets PORT from env or uses 8080 as fallback

print("Executing migrations...")
python manage.py migrate  # Executes Django's migrate command to apply database migrations

# Collect static files from all applications into the STATIC_ROOT directory
print("Executing collectstatic...")
# Run collectstatic without asking for confirmation (--no-input flag)
python manage.py collectstatic --no-input

# Start the Django application using Gunicorn WSGI server
print("Stating Gunicorn with Django")
# Run Gunicorn with the following configuration:
# --capture-output: Capture and redirect stdout/stderr to logging system
# --bind :$PORT: Bind the server to the previously defined PORT on all interfaces
# --workers 3: Use 3 worker processes to handle requests
# cdc.wsgi:application: Path to the WSGI application object
gunicorn --capture-output --bind :$PORT --workers 3 cdc.wsgi:application