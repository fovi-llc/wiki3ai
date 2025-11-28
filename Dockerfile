FROM python:3.13

ARG JUPYTER_PORT=8000
ENV JUPYTER_PORT=${JUPYTER_PORT}

ARG APP_DIR=/app
ENV APP_DIR=${APP_DIR}

RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# RUN pip install --upgrade pip \
# && pip install -Ur jupyterlite==0.7.0rc2 anywidget==0.9.21 ipywidgets jupyterlite-pyodide-kernel jupyter-server jupyterlab==4.5.0 

# RUN pip install nbconvert nbformat

WORKDIR ${APP_DIR}
COPY . ${APP_DIR}

RUN pip install --upgrade pip \
    && pip install uv \
    && uv pip install --system . \
    && uv pip install --system built-in-chat/ \
    && uv pip install --system lite-kernel/ \
    && rm -rf docs .jupyterlite.doit.db \
    && jupyter lite build

# brew install nodejs npm

# pip install uv
# rm .jupyterlite.doit.db 
# uv build lite-kernel/   # don't think needed - the pip install does this
# uv pip install lite-kernel/
# uv pip install .
# jupyter labextension list
# jupyter lab build # not sure if needed
# jupyter lite build  # not needed
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

EXPOSE ${JUPYTER_PORT}
CMD ["jupyter", "lite", "serve", "--port", "${JUPYTER_PORT}"]