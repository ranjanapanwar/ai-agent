FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --no-dev
COPY . .
CMD [ "supervisord", "-c", "supervisord.conf" ]
EXPOSE 8000
EXPOSE 7860