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

WORKDIR ${APP_DIR}
COPY . ${APP_DIR}

RUN pip install --upgrade pip \
    && pip install uv \
    && uv pip install --system . \
    && uv pip install --system built-in-chat/ \
    && uv pip install --system lite-kernel/

RUN rm -rf docs .jupyterlite.doit.db \
    && jupyter lite build

EXPOSE ${JUPYTER_PORT}
CMD ["jupyter", "lite", "serve", "--port", "${JUPYTER_PORT}"]
