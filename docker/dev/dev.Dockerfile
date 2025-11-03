# Pull official base image
FROM python:3.13.5-alpine3.22
# Set working directory
WORKDIR /app
# Don't write out pyc files - improves performance and reduces container size
ENV PYTHONDONTWRITEBYTECODE 1
# No buffering stdin/stdout - ensures logs appear immediately
ENV PYTHONUNBUFFERED 1
ENV UV_COMPILE_BYTECODE=0

# update the alpine linux package index
RUN apk update
# for psutil, a dependencie of marimo. Npm for tailwind. uv for manage system.
RUN apk add --no-cache uv gcc python3-dev musl-dev linux-headers npm
# install xonsh shell - a Python-powered shell language
COPY uv.lock pyproject.toml package.json package-lock.json ./
RUN uv sync --frozen
RUN npm install

# Configurar variáveis de ambiente
ENV PATH="/app/.venv/bin:$PATH"
# Copy start bash script with the instruction on how to start Django.
COPY ./docker/dev/start.xsh /start.xsh
# Convert Windows line endings (CRLF) to Unix (LF) if present and make the script executable
RUN sed -i 's/\r$//g' /start.xsh && chmod +x /start.xsh

# Default command - not used when running through docker compose
# as compose.yaml overrides this with the start.xsh script
CMD ["manage.py", "runserver", "0.0.0.0:8000"]