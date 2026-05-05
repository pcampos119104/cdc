# Pull official base image
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential python3-dev nodejs npm
RUN rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
COPY pyproject.toml uv.lock package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
COPY . .
RUN npm install
RUN npx @tailwindcss/cli -i cdc/static/css/input.css -o cdc/static/css/output.css --minify
RUN rm cdc/static/css/input.css
RUN rm -rf node_modules

# criar o output.css do tailwind

FROM python:3.12-slim
WORKDIR /app

COPY ./docker/prod/start.sh /start.sh
RUN sed -i 's/\r$//g' /start.sh
RUN chmod +x /start.sh
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["/start.sh"]