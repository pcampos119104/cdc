#    Cozinha de Campos project

Project crated using Copier tool.

## Tools, libs, etc. Some time related files.
Versions on pyproject.lock.

- [AlpineJS](https://alpinejs.dev/) JavaScript Framework based on Vue engine
- [Django](https://www.djangoproject.com/) Web framework written in Python
- [django-allauth](https://django-allauth.readthedocs.io/) Authentication and social account login for Django
- [django-environ](https://django-environ.readthedocs.io) Manage .envs in Django
- [django-extensions](https://django-extensions.readthedocs.io/en/latest/) Add manage commands to the django and more
- [django-htmx](https://django-htmx.readthedocs.io/) Django + HTMX integration
- [Docker](https://www.docker.com/) Manage containers for dev environment
    - compose.yaml
    - compose/dev/Dockerfile
    - compose/dev/start
    - .env
- [Gunicorn](https://gunicorn.org/) Python WSGI HTTP Server for UNIX
- [HTMX](https://htmx.org/) htmx gives access to AJAX, CSS Transitions, WebSockets and Server Sent Events directly from
  HTML
- [Just](https://just.systems/) Encapsulate commands for easier use
    - justfile
- [psycopg](https://www.psycopg.org/) Python adapter for Postgres
- [Python](https://www.python.org/) Programming language
- [Sentry](https://sentry.io/) Error tracking and performance monitoring
- [TailwindCSS](https://tailwindcss.com/) CSS Framework
- [Uv](https://docs.astral.sh/uv/) Python packaging and dependency management
    - uv.lock
    - pyproject.toml
- [WhiteNoise](http://whitenoise.evans.io/) Simplified static file serving for Python web apps
- [Xonsh](https://xon.sh/) Python-powered shel


### ...and development

- [django-browser-reload](https://github.com/adamchainz/django-browser-reload) Auto reload the browser when change a
  template
- [Marimo](https://marimo.io/) Notebook for test, prototype, inspections, etc.
    - extras/template.py - Template for a new notebook.
- [Pytest](https://docs.pytest.org/en/8.0.x/) Tools for testing.
- [Pytest-django](https://pytest-django.readthedocs.io/en/latest/) Pytest Plugin for Django
- [ruff](https://docs.astral.sh/ruff/) Linter and code formatter

## Dev environment setup

1. Install Just, Docker and uv (optional). Certify that docker is up and running
2. Copy .env.example to .env, no need for an edition.
3. `$ just build`
4. `$ just mng createsuperuser`

## Run the server for development

1. Ensure that docker is up and running
2. `$ just up`

You can access the Django app on http://0.0.0.0:8000/ and Marimo notebook on http://0.0.0.0:2718/

## On production
add to the .env:

ALLOWED_HOSTS=www.cozinhadecampos.com.br
CSRF_TRUSTED_ORIGINS=https://www.cozinhadecampos.com.br

Create a 'Home page'
