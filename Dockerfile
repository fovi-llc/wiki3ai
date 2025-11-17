FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install jupyterlite anywidget==0.9.21 ipywidgets jupyterlite-pyodide-kernel jupyter-server jupyterlab panel watchfiles wiki3-ai
# RUN pip install nbconvert nbformat

WORKDIR /app
COPY . /app


# brew install nodejs npm
# pip install uv
# uv sync --upgrade-package wiki3-ai
# uv sync --locked --all-extras --dev
# uv run jupyter lab build
# rm -rf _output
# uv run jupyter lite build
# uv run jupyter lite serve 

# https://panel.holoviz.org/how_to/wasm/jupyterlite.html
# jupyter lite build --config jupyter_lite_config.json

# RUN jupyter lite build

EXPOSE 8000
# CMD ["jupyter", "lite", "serve", "--port", "8000"]
