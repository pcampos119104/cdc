#!/bin/bash
# start.sh - Development startup script for the Django application

set -e  # Exit on any error

# Run Django database migrations to ensure database schema is up-to-date
echo "Executando migrações..."
python manage.py migrate

# Start marimo notebook server for development and testing
echo "Iniciando marimo"
# Run marimo in edit mode with the following configuration:
# --host 0.0.0.0: Make the server accessible from any network interface
# -p 2718: Set the port to 2718
# --no-token: Disable authentication token requirement
# --headless: Run without opening a browser window
# &> /dev/null &: Redirect all output to /dev/null and run in the background
marimo edit --host 0.0.0.0 -p 2718 --no-token --headless &> /dev/null &

# Start Tailwind CSS processing server to watch for changes and compile CSS
echo "Iniciando servidor tailwind"
# Run Tailwind CLI with the following configuration:
# -i cdc/static/css/input.css: Input CSS file with Tailwind directives
# -o cdc/static/css/output.css: Output compiled CSS file
# --watch=always: Continuously watch for changes and recompile when detected
# &: Run in the background
npx @tailwindcss/cli -i cdc/static/css/input.css -o cdc/static/css/output.css --watch=always &

echo "Executando collectstatic..."
python manage.py collectstatic --no-input --ignore="css/input.css"

# Start the Django development server
echo "Iniciando servidor Django..."
# Run Django's development server on 0.0.0.0:8000 (accessible from any network interface)
# This is the main process that will run in the foreground
python manage.py runserver 0.0.0.0:8000