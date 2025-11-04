FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install jupyterlite jupyterlite-pyodide-kernel jupyter-server jupyterlab
# RUN pip install nbconvert nbformat

WORKDIR /app
COPY . /app

# RUN jupyter lite build

EXPOSE 8000
# CMD ["jupyter", "lite", "serve", "--port", "8000"]
