FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir jupyterlite jupyterlite-pyodide-kernel

WORKDIR /app
COPY . /app

RUN jupyter lite build

EXPOSE 8000
CMD ["jupyter", "lite", "serve", "--port", "8000"]
