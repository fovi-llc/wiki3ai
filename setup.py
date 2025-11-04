from setuptools import setup, find_packages

setup(
    name="jupyterlite-wiki-addon",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "jupyterlite.addon.v0": [
            "wiki = jupyterlite_wiki_addon.addon:WikiPageAddon",
        ],
    },
    install_requires=[
        "jupyterlite-core>=0.2.0",
        "nbconvert",
        "nbformat",
    ],
    description="JupyterLite addon to generate wiki pages from notebooks",
)
