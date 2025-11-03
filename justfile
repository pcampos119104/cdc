# List all just commands
default:
    just --list

# Build the docker image
build:
    docker compose build
    docker compose run --rm app npm install

# Run the Django app and dependecies services in development mode
up:
    docker compose up -d

# Stop all the containers
down:
    docker compose down

# Enter in the container shell
shell:
    docker compose run --rm app sh

# Run manage.py inside the container
mng +command:
    docker compose run --rm app python manage.py {{ command }}

# Run the tests
test:
    docker compose run --rm app ruff check
    docker compose run --rm app python manage.py collectstatic --noinput --ignore="css/input.css"
    docker compose run --rm app pytest

# Run Ruff for fix errors
format:
    docker compose run --rm app ruff check --fix
    docker compose run --rm app ruff format
