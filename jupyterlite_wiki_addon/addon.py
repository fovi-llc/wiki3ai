from pathlib import Path
import nbformat
from nbconvert import HTMLExporter
from jupyterlite_core.addons.base import BaseAddon
from traitlets import Unicode

class WikiPageAddon(BaseAddon):
    """Generate wiki pages from notebooks"""
    
    addon_id = Unicode("wiki-page-addon")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"[WikiPageAddon] Initializing addon: {self.addon_id}")
    
    def post_build(self, manager):
        """Generate wiki pages after build"""
        print("[WikiPageAddon] post_build called")
        yield dict(
            name="wiki:generate",
            actions=[self.generate_wiki_pages],
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
            
            html_exporter = HTMLExporter(template_name='lab')
            
            for notebook_path in notebooks:
                print(f"[WikiPageAddon] Processing: {notebook_path}")
                
                try:
                    with open(notebook_path, 'r', encoding='utf-8') as f:
                        nb = nbformat.read(f, as_version=4)
                    
                    rel_path = notebook_path.relative_to(files_dir)
                    output_file = wiki_dir / rel_path.with_suffix('.html')
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    lite_url = f"/lab/index.html?path={rel_path}"
                    (body, resources) = html_exporter.from_notebook_node(nb)
                    
                    # Add launch button
                    launch_button = f'''
                    <div style="margin: 20px 0; text-align: center;">
                        <a href="{lite_url}" target="_blank" 
                           style="display: inline-block; padding: 10px 20px; 
                                  background-color: #007bff; color: white; 
                                  text-decoration: none; border-radius: 5px;">
                            🚀 Open in JupyterLite
                        </a>
                    </div>
                    '''
                    
                    body = body.replace('<body>', f'<body>\n{launch_button}')
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(body)
                    
                    print(f"[WikiPageAddon] Generated: {output_file}")
                    
                except Exception as e:
                    print(f"[WikiPageAddon] Error processing {notebook_path}: {e}")
            
            print(f"[WikiPageAddon] Wiki generation complete!")
            
        except Exception as e:
            print(f"[WikiPageAddon] Error in generate_wiki_pages: {e}")
            import traceback
            traceback.print_exc()
