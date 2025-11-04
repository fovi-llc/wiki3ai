from pathlib import Path
import nbformat
from nbconvert import HTMLExporter
from jupyterlite_core.addons.base import BaseAddon

class WikiPageAddon(BaseAddon):
    __all__ = ["post_build"]
    
    def post_build(self, manager):
        yield dict(
            name="wiki:generate",
            actions=[self.generate_wiki_pages],
        )
    
    def generate_wiki_pages(self):
        output_dir = self.manager.output_dir
        files_dir = output_dir / "files"
        wiki_dir = output_dir / "wiki"
        wiki_dir.mkdir(exist_ok=True)
        
        notebooks = list(files_dir.rglob("*.ipynb"))
        html_exporter = HTMLExporter(template_name='lab')
        
        for notebook_path in notebooks:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            rel_path = notebook_path.relative_to(files_dir)
            output_file = wiki_dir / rel_path.with_suffix('.html')
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            lite_url = f"/lab/index.html?path={rel_path}"
            (body, resources) = html_exporter.from_notebook_node(nb)
            
            # Add launch button (same as above)
            body = body.replace('<body>', f'<body>\n<!-- launch button HTML -->')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(body)
