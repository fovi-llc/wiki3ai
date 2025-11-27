FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U jupyterlite==0.7.0rc2 anywidget==0.9.21 ipywidgets jupyterlite-pyodide-kernel jupyter-server jupyterlab==4.5.0 "wiki3-ai>=0.5.1"
# RUN pip install nbconvert nbformat

WORKDIR /app
COPY . /app


# brew install nodejs npm

# pip install uv
# rm .jupyterlite.doit.db 
# uv build lite-kernel/
# uv pip install lite-kernel/
# uv pip install .
# jupyter labextension list
# jupyter lab build
# jupyter lite build
# jupyter lite serve 

# uv sync --locked --all-extras --dev
# uv run jupyter lab build
# rm -rf docs
# cd python-ai
# uv build
# cd ..
# uv run jupyter lab build
# npm --prefix lite-kernel install
# npm --prefix lite-kernel run build
# jupyter labextension install lite-kernel
# mkdir -p pypi/w/wiki3_ai
# cp python-ai/dist/wiki3_ai-*-py3-none-any.whl pypi

# https://panel.holoviz.org/how_to/wasm/jupyterlite.html
# jupyter lite build --config jupyter_lite_config.json

# RUN jupyter lite build

EXPOSE 8000
# CMD ["jupyter", "lite", "serve", "--port", "8000"]
