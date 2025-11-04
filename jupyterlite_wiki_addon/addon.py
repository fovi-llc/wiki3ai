from pathlib import Path
import nbformat
from nbconvert import HTMLExporter
from jupyterlite_core.addons.base import BaseAddon
from traitlets import Unicode

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
                    <div style="margin: 20px 0; text-align: center; background: #f8f9fa; padding: 15px; border-radius: 8px; border: 2px solid #007bff;">
                        <h3 style="margin: 0 0 10px 0; color: #007bff;">📚 Interactive Notebook</h3>
                        <a href="{lite_url}" target="_blank" 
                           style="display: inline-block; padding: 12px 24px; 
                                  background-color: #007bff; color: white; 
                                  text-decoration: none; border-radius: 6px;
                                  font-weight: bold; box-shadow: 0 2px 4px rgba(0,123,255,0.3);">
                            🚀 Open Interactive Version
                        </a>
                        <p style="margin: 10px 0 0 0; font-size: 0.9em; color: #666;">
                            Click above to run this notebook interactively in your browser
                        </p>
                    </div>
                    '''
                    
                    # Find the actual body tag (which may have attributes)
                    import re
                    body_pattern = r'(<body[^>]*>)'
                    match = re.search(body_pattern, body)
                    if match:
                        body_tag = match.group(1)
                        body = body.replace(body_tag, f'{body_tag}\n{launch_button}', 1)
                    else:
                        # Fallback - just add it after the body tag
                        body = body.replace('<body>', f'<body>\n{launch_button}')
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(body)
                    
                    print(f"[WikiPageAddon] Generated: {output_file}")
                    
                except Exception as e:
                    print(f"[WikiPageAddon] Error processing {notebook_path}: {e}")
            
            # Generate index page
            self._generate_index_page(wiki_dir, notebooks)
            
            print(f"[WikiPageAddon] Wiki generation complete!")
            
        except Exception as e:
            print(f"[WikiPageAddon] Error in generate_wiki_pages: {e}")
            import traceback
            traceback.print_exc()
    
    def _generate_index_page(self, wiki_dir, notebook_paths):
        """Generate an index page listing all notebooks"""
        try:
            index_html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Wiki3AI - Notebook Collection</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; 
                           margin: 40px; line-height: 1.6; background: #f8f9fa; }
                    .container { max-width: 800px; margin: 0 auto; background: white; 
                                padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                    h1 { color: #007bff; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
                    .notebook-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                                   gap: 20px; margin: 30px 0; }
                    .notebook-card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; 
                                   background: #f8f9fa; transition: transform 0.2s, box-shadow 0.2s; }
                    .notebook-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,123,255,0.2); }
                    .notebook-title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; color: #333; }
                    .notebook-links { margin-top: 15px; }
                    .notebook-links a { display: inline-block; margin-right: 10px; margin-bottom: 8px;
                                      padding: 8px 16px; text-decoration: none; border-radius: 4px; font-size: 0.9em; }
                    .btn-view { background: #007bff; color: white; }
                    .btn-interactive { background: #28a745; color: white; }
                    .btn-view:hover, .btn-interactive:hover { opacity: 0.8; }
                    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; 
                            text-align: center; color: #666; font-size: 0.9em; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📚 Wiki3AI Notebook Collection</h1>
                    <p>Welcome to the Wiki3AI notebook collection. Below you'll find interactive Jupyter notebooks 
                       covering various topics including WebLLM, AI in the browser, and more.</p>
                    
                    <div class="notebook-grid">
            """
            
            files_dir = Path(self.manager.output_dir) / "files"
            
            for notebook_path in notebook_paths:
                try:
                    # Read notebook to get title from first markdown cell
                    with open(notebook_path, 'r', encoding='utf-8') as f:
                        nb = nbformat.read(f, as_version=4)
                    
                    # Extract title from first markdown cell or use filename
                    title = notebook_path.stem.replace('-', ' ').replace('_', ' ').title()
                    description = "Interactive Jupyter notebook"
                    
                    for cell in nb.cells:
                        if cell.cell_type == 'markdown' and cell.source.strip():
                            lines = cell.source.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line.startswith('# '):
                                    title = line[2:].strip()
                                    break
                                elif line.startswith('## ') or line.startswith('### '):
                                    title = line.lstrip('#').strip()
                                    break
                            # Get description from first paragraph
                            desc_lines = [l.strip() for l in lines if l.strip() and not l.startswith('#')]
                            if desc_lines:
                                description = desc_lines[0][:200] + ('...' if len(desc_lines[0]) > 200 else '')
                            break
                    
                    rel_path = notebook_path.relative_to(files_dir)
                    html_file = rel_path.with_suffix('.html')
                    lite_url = f"/lab/index.html?path={rel_path}"
                    
                    index_html += f'''
                        <div class="notebook-card">
                            <div class="notebook-title">{title}</div>
                            <div class="notebook-description">{description}</div>
                            <div class="notebook-links">
                                <a href="{html_file}" class="btn-view">📖 View Static</a>
                                <a href="{lite_url}" target="_blank" class="btn-interactive">🚀 Run Interactive</a>
                            </div>
                        </div>
                    '''
                except Exception as e:
                    print(f"[WikiPageAddon] Error processing {notebook_path} for index: {e}")
            
            index_html += """
                    </div>
                    
                    <div class="footer">
                        <p>Generated by Wiki3AI JupyterLite addon</p>
                        <p>🚀 <a href="/lab/index.html" target="_blank">Open JupyterLite Lab</a> | 
                           📁 <a href="/files" target="_blank">Browse Files</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            index_file = wiki_dir / "index.html"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_html)
            
            print(f"[WikiPageAddon] Generated index page: {index_file}")
            
        except Exception as e:
            print(f"[WikiPageAddon] Error generating index page: {e}")
            import traceback
            traceback.print_exc()
