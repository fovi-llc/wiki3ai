FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install jupyterlite anywidget ipywidgets jupyterlite-pyodide-kernel jupyter-server jupyterlab panel watchfiles
# RUN pip install nbconvert nbformat

WORKDIR /app
COPY . /app

# https://panel.holoviz.org/how_to/wasm/jupyterlite.html
# jupyter lite build --config jupyter_lite_config.json

# RUN jupyter lite build

EXPOSE 8000
# CMD ["jupyter", "lite", "serve", "--port", "8000"]
