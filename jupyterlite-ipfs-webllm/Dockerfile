FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir jupyterlite jupyterlite-pyodide-kernel jupyter_server

WORKDIR /app
COPY . /app

RUN jupyter lite build --output-archive=app-jupyterlite.tgz

EXPOSE 8000
CMD ["jupyter", "lite", "serve", "--port", "8000"]
