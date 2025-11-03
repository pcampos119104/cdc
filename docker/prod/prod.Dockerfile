# Pull official base image
FROM python:3.13.5-alpine3.22 AS builder

# Set working directory
WORKDIR /app
RUN apk update
RUN apk add --no-cache gcc python3-dev musl-dev linux-headers curl uv npm

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

FROM python:3.13.5-alpine3.22
WORKDIR /app

COPY ./docker/prod/start.xsh /start.xsh
RUN sed -i 's/\r$//g' /start.xsh
RUN chmod +x /start.xsh
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["/start.xsh"]