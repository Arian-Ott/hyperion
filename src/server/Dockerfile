FROM python:3.14-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY src/server /app
COPY uv.lock  /app
COPY pyproject.toml /app
ENV UV_NO_DEV=1
WORKDIR /app
RUN uv sync --extra server
EXPOSE 9000
CMD 



