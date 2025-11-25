from pathlib import Path
import html
import os
from urllib.parse import quote

import nbformat
from nbconvert import HTMLExporter
from jupyterlite_core.addons.base import BaseAddon

class WikiPageAddon(BaseAddon):
    """Generate wiki pages from notebooks"""
    
    __all__ = ["post_build"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"[WikiPageAddon] Initializing addon")
    
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
            behavior_script = self._behavior_script()
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
                        "wiki_behavior_script": behavior_script,
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
            head_assets = self._head_assets(relative_root)
            behavior_script = self._behavior_script()

            items_html = []
            for entry in sorted(entries, key=lambda item: item['rel_path'].as_posix()):
                rel_path = entry['rel_path']
                rel_display = html.escape(rel_path.as_posix())
                html_rel = entry['html_rel_path']
                html_href = quote(html_rel.as_posix(), safe='/')
                rel_path_url = quote(rel_path.as_posix(), safe='/')
                static_path = entry['static_output']
                static_href = '/' + quote(static_path.as_posix(), safe='/')
                edit_href = f"/notebooks/index.html?path={rel_path_url}"
                lab_href = f"/lab/index.html?path={rel_path_url}"
                download_href = f"/files/{rel_path_url}"
                title_attr = html.escape(entry['title']) if entry.get('title') else rel_display

                items_html.append(
                    (
                        "        <li class=\"wiki-row\" role=\"listitem\">\n"
                        "          <div class=\"wiki-actions\" role=\"group\" aria-label=\"Actions\">\n"
                        f"            <a class=\"jp-Button wiki-action-button\" href=\"{html_href}\">open</a>\n"
                        f"            <a class=\"jp-Button wiki-action-button\" href=\"{edit_href}\" target=\"_blank\" rel=\"noopener noreferrer\">edit</a>\n"
                        f"            <a class=\"jp-Button wiki-action-button\" href=\"{lab_href}\" target=\"_blank\" rel=\"noopener noreferrer\">lab</a>\n"
                        f"            <a class=\"jp-Button wiki-action-button\" href=\"{download_href}\" download aria-label=\"Download\" title=\"Download\">down</a>\n"
                        f"            <button type=\"button\" class=\"jp-Button wiki-action-button\" data-share=\"{static_href}\" aria-label=\"Copy share link\">share</button>\n"
                        "          </div>\n"
                        f"          <span class=\"wiki-name\"><a href=\"{html_href}\" title=\"{title_attr}\">{rel_display}</a></span>\n"
                        "        </li>\n"
                    )
                )

            list_markup = ''.join(items_html)

            index_html = (
                "<!DOCTYPE html>\n"
                "<html lang=\"en\">\n"
                "<head>\n"
                "  <meta charset=\"utf-8\" />\n"
                "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n"
                "  <title>Wiki Index</title>\n"
                f"{head_assets}"
                "</head>\n"
                "<body class=\"jp-mod-light\" data-jp-theme-light=\"true\" data-jp-theme-name=\"JupyterLite Light\">\n"
                "  <div class=\"wiki-toolbar\" role=\"toolbar\" aria-label=\"Wiki navigation\">\n"
                "    <div class=\"wiki-toolbar-left\">\n"
                "      <a class=\"jp-Button wiki-home\" href=\"/\">home</a>\n"
                "      <span class=\"wiki-toolbar-title\">Wiki3.ai index</span>\n"
                "    </div>\n"
                "    <div class=\"wiki-toolbar-actions\" role=\"group\" aria-label=\"Global actions\">\n"
                "      <a class=\"jp-Button wiki-action-button\" href=\"/tree/index.html\">Files</a>\n"
                "      <a class=\"jp-Button wiki-action-button\" href=\"/lab/index.html\" target=\"_blank\" rel=\"noopener noreferrer\">lab</a>\n"
                "    </div>\n"
                "  </div>\n"
                "  <main class=\"wiki-main\">\n"
                "    <ul class=\"wiki-list\" role=\"list\">\n"
                f"{list_markup}"
                "    </ul>\n"
                "  </main>\n"
                f"  {self._share_status_html()}\n"
                f"  {behavior_script}"
                "</body>\n"
                "</html>\n"
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

    def _head_assets(self, relative_root: Path) -> str:
        """Return shared theme links and minimal styles."""
        theme_base = relative_root / "build" / "themes" / "@jupyterlab"
        light_css = (theme_base / "theme-light-extension" / "index.css").as_posix()
        dark_css = (theme_base / "theme-dark-extension" / "index.css").as_posix()
        return (
            f"  <link rel=\"stylesheet\" href=\"{light_css}\" media=\"(prefers-color-scheme: light), (prefers-color-scheme: no-preference)\" />\n"
            f"  <link rel=\"stylesheet\" href=\"{dark_css}\" media=\"(prefers-color-scheme: dark)\" />\n"
            "  <style>\n"
            "    :root { color-scheme: light dark; }\n"
            "    body { margin: 0; }\n"
            "    body.jp-mod-light, body.jp-mod-dark { background: var(--jp-layout-color0); color: var(--jp-ui-font-color1); }\n"
            "    .jp-Button, .jp-Button:visited {\n"
            "      display: inline-flex;\n"
            "      align-items: center;\n"
            "      justify-content: center;\n"
            "      gap: 0.25rem;\n"
            "      padding: 0.25rem 0.75rem;\n"
            "      border-radius: 4px;\n"
            "      border: 1px solid var(--jp-border-color2);\n"
            "      background: var(--jp-layout-color2);\n"
            "      color: inherit;\n"
            "      text-decoration: none;\n"
            "      font-size: var(--jp-ui-font-size1, 14px);\n"
            "      line-height: 1.4;\n"
            "      cursor: pointer;\n"
            "    }\n"
            "    .jp-Button:hover, .jp-Button:focus {\n"
            "      border-color: var(--jp-brand-color1);\n"
            "      text-decoration: none;\n"
            "    }\n"
            "    .jp-Button:focus-visible {\n"
            "      outline: 2px solid var(--jp-brand-color1);\n"
            "      outline-offset: 2px;\n"
            "    }\n"
            "    button.jp-Button {\n"
            "      appearance: none;\n"
            "      -webkit-appearance: none;\n"
            "    }\n"
            "    .wiki-toolbar {\n"
            "      position: sticky;\n"
            "      top: 0;\n"
            "      z-index: 1000;\n"
            "      display: flex;\n"
            "      align-items: center;\n"
            "      justify-content: space-between;\n"
            "      gap: 1rem;\n"
            "      padding: 0.75rem 1rem;\n"
            "      background: var(--jp-layout-color1);\n"
            "      border-bottom: 1px solid var(--jp-border-color2);\n"
            "    }\n"
            "    .wiki-toolbar-left {\n"
            "      display: flex;\n"
            "      align-items: center;\n"
            "      gap: 0.75rem;\n"
            "      min-width: 0;\n"
            "    }\n"
            "    .wiki-toolbar-title {\n"
            "      font-weight: 600;\n"
            "      font-size: var(--jp-ui-font-size2, 16px);\n"
            "      white-space: nowrap;\n"
            "      overflow: hidden;\n"
            "      text-overflow: ellipsis;\n"
            "    }\n"
            "    .wiki-toolbar-actions {\n"
            "      display: flex;\n"
            "      flex-wrap: wrap;\n"
            "      gap: 0.5rem;\n"
            "      align-items: center;\n"
            "    }\n"
            "    .wiki-main {\n"
            "      max-width: 960px;\n"
            "      margin: 0 auto;\n"
            "      padding: 1rem 1.5rem;\n"
            "    }\n"
            "    .wiki-list {\n"
            "      list-style: none;\n"
            "      margin: 0;\n"
            "      padding: 0;\n"
            "    }\n"
            "    .wiki-row {\n"
            "      display: grid;\n"
            "      grid-template-columns: auto 1fr;\n"
            "      gap: 1rem;\n"
            "      align-items: center;\n"
            "      padding: 0.5rem 0;\n"
            "      border-bottom: 1px solid var(--jp-border-color2);\n"
            "    }\n"
            "    .wiki-name {\n"
            "      min-width: 0;\n"
            "    }\n"
            "    .wiki-name a {\n"
            "      color: var(--jp-content-link-color, inherit);\n"
            "      text-decoration: none;\n"
            "      word-break: break-all;\n"
            "    }\n"
            "    .wiki-name a:hover { text-decoration: underline; }\n"
            "    .wiki-action-button { text-transform: lowercase; }\n"
            "    .wiki-share-success {\n"
            "      box-shadow: 0 0 0 2px var(--jp-success-color1);\n"
            "    }\n"
            "    .wiki-sr-only {\n"
            "      position: absolute;\n"
            "      width: 1px;\n"
            "      height: 1px;\n"
            "      padding: 0;\n"
            "      margin: -1px;\n"
            "      overflow: hidden;\n"
            "      clip: rect(0, 0, 0, 0);\n"
            "      border: 0;\n"
            "    }\n"
            "    .wiki-actions {\n"
            "      display: inline-flex;\n"
            "      flex-wrap: wrap;\n"
            "      gap: 0.5rem;\n"
            "      align-items: center;\n"
            "    }\n"
            "    .wiki-toolbar + * {\n"
            "      padding-top: 0.75rem;\n"
            "    }\n"
            "  </style>\n"
        )

    def _share_status_html(self) -> str:
        """Hidden live region for announcing share actions."""
        return '<div id="wiki-share-status" class="wiki-sr-only" aria-live="polite"></div>'

    def _behavior_script(self) -> str:
        """Return the inline script that powers theme toggles and share buttons."""
        return (
            "<script>\n"
            "(function() {\n"
            "  const body = document.body;\n"
            "  const status = document.getElementById('wiki-share-status');\n"
            "  const applyTheme = (isDark) => {\n"
            "    body.classList.toggle('jp-mod-dark', isDark);\n"
            "    body.classList.toggle('jp-mod-light', !isDark);\n"
            "    body.setAttribute('data-jp-theme-light', String(!isDark));\n"
            "    body.setAttribute('data-jp-theme-name', isDark ? 'JupyterLab Dark' : 'JupyterLab Light');\n"
            "  };\n"
            "  const media = window.matchMedia('(prefers-color-scheme: dark)');\n"
            "  applyTheme(media.matches);\n"
            "  if (media.addEventListener) {\n"
            "    media.addEventListener('change', (event) => applyTheme(event.matches));\n"
            "  } else if (media.addListener) {\n"
            "    media.addListener((event) => applyTheme(event.matches));\n"
            "  }\n"
            "  const announce = (message) => {\n"
            "    if (!status) {\n"
            "      return;\n"
            "    }\n"
            "    status.textContent = message;\n"
            "    window.setTimeout(() => { status.textContent = ''; }, 1500);\n"
            "  };\n"
            "  body.addEventListener('click', (event) => {\n"
            "    const trigger = event.target.closest('[data-share]');\n"
            "    if (!trigger) {\n"
            "      return;\n"
            "    }\n"
            "    event.preventDefault();\n"
            "    const shareTarget = trigger.getAttribute('data-share') || window.location.pathname;\n"
            "    const url = new URL(shareTarget, window.location.origin).toString();\n"
            "    if (navigator.clipboard && navigator.clipboard.writeText) {\n"
            "      navigator.clipboard.writeText(url).then(() => {\n"
            "        trigger.classList.add('wiki-share-success');\n"
            "        window.setTimeout(() => trigger.classList.remove('wiki-share-success'), 1500);\n"
            "        announce('Link copied to clipboard.');\n"
            "      }).catch(() => {\n"
            "        window.prompt('Copy this link', url);\n"
            "      });\n"
            "    } else {\n"
            "      window.prompt('Copy this link', url);\n"
            "    }\n"
            "  });\n"
            "})();\n"
            "</script>\n"
        )
