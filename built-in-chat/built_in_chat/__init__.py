# built-in-chat - Built-in AI Chat kernel for JupyterLite using Chrome's built-in AI
# This is a JupyterLab extension with no Python code.
# The extension is distributed via shared-data in the wheel.

__version__ = "1.0.0"


def _jupyter_labextension_paths():
    """Return metadata about the JupyterLab extension."""
    return [{
        "src": "built_in_chat/labextension",
        "dest": "@wiki3-ai/built-in-chat"
    }]
