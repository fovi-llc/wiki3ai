FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install JupyterLite and necessary Python packages
RUN pip install --no-cache-dir jupyterlite jupyterlite-pyodide-kernel jupyter_server

# Build the JupyterLite site with the specified Pyodide version
RUN jupyter lite build --output-dir /app/build

# Expose the default port
EXPOSE 8000

# Serve the JupyterLite site
CMD ["jupyter", "lite", "serve", "--port", "8000"]
