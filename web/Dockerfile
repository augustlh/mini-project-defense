FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY . /app

# Downloads dependencies
RUN uv sync --locked

# Flask is on port 5000
EXPOSE 5000

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "app:app"]