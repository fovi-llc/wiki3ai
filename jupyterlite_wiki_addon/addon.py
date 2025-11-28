from importlib.metadata import version
from pathlib import Path
import html
import os
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader
import nbformat
from nbconvert import HTMLExporter
from jupyterlite_core.addons.base import BaseAddon

# Get version from package metadata - bump in pyproject.toml to force
# regeneration of all wiki pages when templates or conversion logic changes
__version__ = version("wiki3-ai-site")

class WikiPageAddon(BaseAddon):
    """Generate wiki pages from notebooks"""
    
    __all__ = ["build", "post_build"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._template_dir = Path(__file__).parent / "templates"
        self._index_template = self._template_dir / "wiki_index.html.j2"
    
    def build(self, manager):
        """Copy static assets to output directory"""
        src = self._template_dir / "wiki_behavior.js"
        dest = manager.output_dir / "static" / "wiki_behavior.js"
        
        yield self.task(
            name="copy:wiki_behavior.js",
            doc="copy wiki behavior script to static",
            file_dep=[src],
            targets=[dest],
            actions=[
                (self.copy_one, [src, dest]),
            ],
        )
    
    def post_build(self, manager):
        """Generate wiki pages after build"""
        output_dir = Path(manager.output_dir)
        files_dir = output_dir / "files"
        wiki_dir = output_dir / "wiki"
        
        if not files_dir.exists():
            return
        
        notebooks = list(files_dir.rglob("*.ipynb"))
        if not notebooks:
            return
        
        wiki_dir.mkdir(exist_ok=True)
        
        # Check if addon version changed - if so, clear old outputs to force rebuild
        version_file = wiki_dir / ".wiki_addon_version"
        old_version = version_file.read_text().strip() if version_file.exists() else None
        
        if old_version != __version__:
            print(f"[WikiPageAddon] Version changed ({old_version} -> {__version__}), regenerating all pages")
            for html_file in wiki_dir.glob("**/*.html"):
                html_file.unlink()
            version_file.write_text(__version__)
        
        # Yield a task for each notebook
        all_output_files = []
        for notebook_path in notebooks:
            rel_path = notebook_path.relative_to(files_dir)
            output_file = wiki_dir / rel_path.with_suffix('.html')
            all_output_files.append(output_file)
            
            yield self.task(
                name=f"convert:{rel_path.as_posix()}",
                doc=f"convert {rel_path} to HTML",
                file_dep=[notebook_path],
                targets=[output_file],
                actions=[
                    (self._convert_notebook, [notebook_path, output_file, files_dir, output_dir]),
                ],
            )
        
        # Yield task for index page (depends on all notebook outputs)
        index_file = wiki_dir / "index.html"
        yield self.task(
            name="generate:index",
            doc="generate wiki index page",
            file_dep=[self._index_template] + all_output_files,
            targets=[index_file],
            actions=[
                (self._generate_index_page, [wiki_dir, files_dir, output_dir]),
            ],
        )
    
    def _convert_notebook(self, notebook_path, output_file, files_dir, output_dir):
        """Convert a single notebook to HTML"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        notebook_title = self._extract_notebook_title(nb, notebook_path)
        rel_path = notebook_path.relative_to(files_dir)
        static_output = output_file.relative_to(output_dir)
        rel_path_url = quote(rel_path.as_posix(), safe='/')
        
        html_exporter = HTMLExporter(
            template_name='wiki',
            extra_template_basedirs=[str(self._template_dir)],
        )
        
        resources = {
            "metadata": {"name": notebook_path.stem},
            "wiki_toolbar": {
                "title": notebook_title,
                "home_href": "/",
                "actions": [
                    {
                        "kind": "link",
                        "label": "edit",
                        "href": f"/notebooks/index.html?path={rel_path_url}",
                        "new_tab": True,
                        "download": False,
                    },
                    {
                        "kind": "link",
                        "label": "lab",
                        "href": f"/lab/index.html?path={rel_path_url}",
                        "new_tab": True,
                        "download": False,
                    },
                    {
                        "kind": "link",
                        "label": "down",
                        "href": f"/files/{rel_path_url}",
                        "new_tab": False,
                        "download": True,
                    },
                    {
                        "kind": "button",
                        "label": "share",
                        "share_href": '/' + quote(static_output.as_posix(), safe='/'),
                        "aria_label": "Copy share link",
                    },
                ],
            },
            "wiki_behavior_script_url": "/static/wiki_behavior.js",
        }

        body, _ = html_exporter.from_notebook_node(nb, resources=resources)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(body)
        
        print(f"[WikiPageAddon] Generated: {output_file}")
    
    def _generate_index_page(self, wiki_dir, files_dir, output_dir):
        """Generate an index page listing all notebooks"""
        relative_root = Path(os.path.relpath(output_dir, wiki_dir))
        theme_base = relative_root / "build" / "themes" / "@jupyterlab"
        light_css = (theme_base / "theme-light-extension" / "index.css").as_posix()
        dark_css = (theme_base / "theme-dark-extension" / "index.css").as_posix()

        # Scan for all HTML files in wiki_dir (excluding index.html)
        html_files = [f for f in wiki_dir.rglob("*.html") if f.name != "index.html"]
        
        # Build entries from the HTML files
        template_entries = []
        for html_file in sorted(html_files, key=lambda f: f.relative_to(wiki_dir).as_posix()):
            html_rel_path = html_file.relative_to(wiki_dir)
            # Corresponding notebook path
            nb_rel_path = html_rel_path.with_suffix('.ipynb')
            notebook_path = files_dir / nb_rel_path
            
            # Extract title from notebook if it exists
            title = nb_rel_path.stem.replace('-', ' ').replace('_', ' ').title()
            if notebook_path.exists():
                try:
                    with open(notebook_path, 'r', encoding='utf-8') as f:
                        nb = nbformat.read(f, as_version=4)
                    title = self._extract_notebook_title(nb, notebook_path)
                except Exception:
                    pass
            
            rel_display = html.escape(nb_rel_path.as_posix())
            html_href = quote(html_rel_path.as_posix(), safe='/')
            rel_path_url = quote(nb_rel_path.as_posix(), safe='/')
            static_output = html_file.relative_to(output_dir)
            static_href = '/' + quote(static_output.as_posix(), safe='/')
            title_attr = html.escape(title)

            template_entries.append({
                'html_href': html_href,
                'edit_href': f"/notebooks/index.html?path={rel_path_url}",
                'lab_href': f"/lab/index.html?path={rel_path_url}",
                'download_href': f"/files/{rel_path_url}",
                'static_href': static_href,
                'title_attr': title_attr,
                'rel_display': rel_display,
            })

        # Load and render Jinja2 template
        env = Environment(
            loader=FileSystemLoader(str(self._template_dir)),
            autoescape=True,
        )
        template = env.get_template("wiki_index.html.j2")

        index_html = template.render(
            title="Wiki Index",
            toolbar_title="Wiki3.ai index",
            light_css=light_css,
            dark_css=dark_css,
            entries=template_entries,
            behavior_script_url="/static/wiki_behavior.js",
        )

        index_file = wiki_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print(f"[WikiPageAddon] Generated index page: {index_file}")

    def _extract_notebook_title(self, nb, notebook_path):
        """Best effort to pull a title from the notebook."""
        try:
            for cell in nb.cells:
                if cell.get('cell_type') != 'markdown':
                    continue
                source = cell.get('source') or ''
                lines = [line.strip() for line in source.splitlines() if line.strip()]
                for line in lines:
                    if line.startswith('#'):
                        return line.lstrip('#').strip()
            return notebook_path.stem.replace('-', ' ').replace('_', ' ').title()
        except Exception:
            return notebook_path.stem
