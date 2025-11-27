from pathlib import Path
import html
import os
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader
import nbformat
from nbconvert import HTMLExporter
from jupyterlite_core.addons.base import BaseAddon

class WikiPageAddon(BaseAddon):
    """Generate wiki pages from notebooks"""
    
    __all__ = ["build", "post_build"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"[WikiPageAddon] Initializing addon")
    
    def build(self, manager):
        """Copy static assets to output directory"""
        template_dir = Path(__file__).parent / "templates"
        src = template_dir / "wiki_behavior.js"
        dest = manager.output_dir / "static" / "wiki_behavior.js"
        
        yield self.task(
            name="copy:wiki_behavior.js",
            doc="copy wiki behavior script to static",
            actions=[
                (self.copy_one, [src, dest]),
            ],
        )
    
    def post_build(self, manager):
        """Generate wiki pages after build"""
        print("[WikiPageAddon] post_build called")
        yield dict(
            name="wiki:generate",
            actions=[(self.generate_wiki_pages, [])],
        )
    
    def generate_wiki_pages(self):
        """Generate HTML wiki pages from notebooks"""
        print("[WikiPageAddon] Generating wiki pages...")
        
        try:
            output_dir = Path(self.manager.output_dir)
            files_dir = output_dir / "files"
            wiki_dir = output_dir / "wiki"
            
            print(f"[WikiPageAddon] Output dir: {output_dir}")
            print(f"[WikiPageAddon] Files dir: {files_dir}")
            print(f"[WikiPageAddon] Wiki dir: {wiki_dir}")
            
            wiki_dir.mkdir(exist_ok=True)
            
            if not files_dir.exists():
                print(f"[WikiPageAddon] Files directory doesn't exist: {files_dir}")
                return
            
            notebooks = list(files_dir.rglob("*.ipynb"))
            print(f"[WikiPageAddon] Found {len(notebooks)} notebooks")

            if not notebooks:
                print("[WikiPageAddon] No notebooks found to convert")
                return
            
            template_dir = Path(__file__).parent / "templates"
            html_exporter = HTMLExporter(
                template_name='wiki',
                extra_template_basedirs=[str(template_dir)],
            )
            
            index_entries = []
            
            for notebook_path in notebooks:
                print(f"[WikiPageAddon] Processing: {notebook_path}")
                
                try:
                    with open(notebook_path, 'r', encoding='utf-8') as f:
                        nb = nbformat.read(f, as_version=4)
                    
                    notebook_title = self._extract_notebook_title(nb, notebook_path)
                    rel_path = notebook_path.relative_to(files_dir)
                    output_file = wiki_dir / rel_path.with_suffix('.html')
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    static_output = output_file.relative_to(output_dir)
                    rel_path_url = quote(rel_path.as_posix(), safe='/')
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

                    index_entries.append(
                        dict(
                            rel_path=rel_path,
                            html_rel_path=rel_path.with_suffix('.html'),
                            static_output=static_output,
                            title=notebook_title,
                        )
                    )
                    
                except Exception as e:
                    print(f"[WikiPageAddon] Error processing {notebook_path}: {e}")
            
            # Generate index page
            self._generate_index_page(wiki_dir, index_entries, output_dir)
            
            print(f"[WikiPageAddon] Wiki generation complete!")
            
        except Exception as e:
            print(f"[WikiPageAddon] Error in generate_wiki_pages: {e}")
            import traceback
            traceback.print_exc()
    
    def _generate_index_page(self, wiki_dir, entries, output_dir):
        """Generate an index page listing all notebooks"""
        try:
            relative_root = Path(os.path.relpath(output_dir, wiki_dir))
            theme_base = relative_root / "build" / "themes" / "@jupyterlab"
            light_css = (theme_base / "theme-light-extension" / "index.css").as_posix()
            dark_css = (theme_base / "theme-dark-extension" / "index.css").as_posix()

            # Prepare template entries
            template_entries = []
            for entry in sorted(entries, key=lambda item: item['rel_path'].as_posix()):
                rel_path = entry['rel_path']
                rel_display = html.escape(rel_path.as_posix())
                html_rel = entry['html_rel_path']
                html_href = quote(html_rel.as_posix(), safe='/')
                rel_path_url = quote(rel_path.as_posix(), safe='/')
                static_path = entry['static_output']
                static_href = '/' + quote(static_path.as_posix(), safe='/')
                title_attr = html.escape(entry['title']) if entry.get('title') else rel_display

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
            template_dir = Path(__file__).parent / "templates"
            env = Environment(
                loader=FileSystemLoader(str(template_dir)),
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
            
        except Exception as e:
            print(f"[WikiPageAddon] Error generating index page: {e}")
            import traceback
            traceback.print_exc()

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
