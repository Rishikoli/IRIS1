
import os
import json
import datetime

# Configuration
PROJECT_ROOT = "/home/aditya/IRIS1/frontend"
OUTPUT_FILE = "/home/aditya/.gemini/antigravity/brain/7dd913dd-55f5-469f-a71e-74da9c1a5644/frontend_tech_report.html"

def get_dependencies():
    with open(os.path.join(PROJECT_ROOT, "package.json"), 'r') as f:
        data = json.load(f)
    return data.get('dependencies', {}), data.get('devDependencies', {})

def generate_file_tree(startpath):
    tree_html = "<ul class='tree'>"
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        base = os.path.basename(root)
        if base in ['node_modules', '.next', '.git', '__pycache__']:
            del dirs[:]
            continue
        
        tree_html += f"<li><span class='folder'>{base}/</span><ul>"
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree_html += f"<li><span class='file'>{f}</span></li>"
        tree_html += "</ul></li>"
    tree_html += "</ul>"
    # Basic cleanup of empty uls
    tree_html = tree_html.replace("<ul></ul>", "")
    return tree_html

def generate_report():
    deps, dev_deps = get_dependencies()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IRIS1 Frontend Technical Report</title>
        <style>
            :root {{
                --primary: #2563eb;
                --secondary: #475569;
                --bg: #ffffff;
                --text: #1e293b;
                --border: #e2e8f0;
            }}
            body {{
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: var(--text);
                max-width: 1000px;
                margin: 0 auto;
                padding: 40px;
                background: var(--bg);
            }}
            h1, h2, h3 {{ color: #0f172a; border-bottom: 2px solid var(--border); padding-bottom: 10px; margin-top: 40px; }}
            h1 {{ font-size: 2.5em; border-bottom: 4px solid var(--primary); }}
            .metadata {{ color: var(--secondary); margin-bottom: 40px; }}
            
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid var(--border); }}
            th {{ background-color: #f8fafc; font-weight: 600; color: #334155; }}
            tr:hover {{ background-color: #f1f5f9; }}
            
            .badge {{ 
                display: inline-block; padding: 2px 8px; border-radius: 4px; 
                font-size: 0.85em; font-weight: 500; background: #e0f2fe; color: #0369a1; 
            }}
            
            .component-card {{
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                background: #f8fafc;
            }}
            .component-card h4 {{ margin-top: 0; color: var(--primary); }}
            
            /* Tree View */
            ul.tree, ul.tree ul {{ list-style-type: none; margin: 0; padding: 0; }}
            ul.tree ul {{ margin-left: 20px; }}
            ul.tree li {{ margin: 5px 0; padding-left: 20px; position: relative; }}
            ul.tree li::before {{ content: ''; position: absolute; top: 10px; left: 0; width: 15px; height: 1px; background: #cbd5e1; }}
            ul.tree li::after {{ content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 1px; background: #cbd5e1; }}
            ul.tree li:last-child::after {{ height: 10px; }}
            .folder {{ font-weight: bold; color: #d97706; }}
            .file {{ color: #475569; }}

            @media print {{
                body {{ max-width: 100%; padding: 0; }}
                h1 {{ margin-top: 0; }}
                .no-print {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>IRIS1 Frontend Technical Architecture</h1>
            <div class="metadata">
                <p><strong>Generated:</strong> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p><strong>Version:</strong> 1.0.0</p>
                <p><strong>Framework:</strong> Next.js 15 App Router</p>
            </div>
        </div>

        <h2>1. Executive Summary</h2>
        <p>
            The IRIS1 frontend is a high-performance, interactive financial forensics dashboard built with 
            <strong>Next.js 15</strong> and <strong>React 19</strong>. It leverages advanced WebGL visualizations 
            (Three.js, React Sphere) and network graph analysis (React Flow, ShellHunter3D) to detect financial anomalies 
            and fraud rings in real-time. The UI follows a modern "Neumorphic" design language implemented with 
            <strong>Tailwind CSS v4</strong>.
        </p>

        <h2>2. Architecture & Data Flow</h2>
        <div class="component-card">
            <h3>Core Stack</h3>
            <ul>
                <li><strong>Runtime:</strong> Node.js / Browser (Universal Rendering)</li>
                <li><strong>Routing:</strong> Next.js App Router (File-system based)</li>
                <li><strong>State Management:</strong> React Context + Local State (Zustand/Redux not required due to atomic component design)</li>
                <li><strong>Styling:</strong> Tailwind CSS v4 + PostCSS + CSS Modules for complex animations</li>
            </ul>
        </div>

        <h2>3. Component Deep Dives</h2>
        
        <div class="component-card">
            <h4>🌊 Liquid Ether Simulation (LiquidEther.tsx)</h4>
            <p>A custom WebGL fluid dynamics engine used for the landing page background.</p>
            <ul>
                <li><strong>Technology:</strong> Three.js, Custom GLSL Shaders</li>
                <li><strong>Technique:</strong> FBO (Frame Buffer Object) ping-ponging for physics simulation.</li>
                <li><strong>Optimization:</strong> Adaptive resolution scaling checks device capabilities and reduced-motion preferences.</li>
            </ul>
        </div>

        <div class="component-card">
            <h4>🕷️ Shell Hunter 3D (ShellHunter3D.tsx)</h4>
            <p>Force-directed 3D graph analysis tool for detecting circular trading loops.</p>
            <ul>
                <li><strong>Technology:</strong> react-force-graph-3d, Three.js</li>
                <li><strong>Features:</strong> 
                    <ul>
                        <li>Cycle Detection algorithms highlighting fraud rings.</li>
                        <li>3D Camera controls with auto-focus.</li>
                        <li>Particle effects on suspicious transaction edges.</li>
                    </ul>
                </li>
            </ul>
        </div>
        
        <div class="component-card">
            <h4>📊 Forensic Network Graph (ForensicGraph.tsx)</h4>
            <p>2D interactive node graph for relationship mapping.</p>
            <ul>
                <li><strong>Technology:</strong> React Flow</li>
                <li><strong>Features:</strong> Custom node types ('CyberNode') and interactive zoom/pan controls.</li>
            </ul>
        </div>

        <h2>4. Comprehensive Dependency Matrix</h2>
        <h3>Production Dependencies</h3>
        <table>
            <thead><tr><th>Package</th><th>Version</th><th>Purpose</th></tr></thead>
            <tbody>
    """
    
    for name, version in sorted(deps.items()):
        purpose = "Utility"
        if "react" in name: purpose = "UI Library"
        if "three" in name or "d3" in name or "chart" in name or "graph" in name: purpose = "Visualization"
        if "next" in name: purpose = "Framework"
        if "axios" in name: purpose = "Networking"
        
        html_content += f"<tr><td><strong>{name}</strong></td><td><span class='badge'>{version}</span></td><td>{purpose}</td></tr>"

    html_content += """
            </tbody>
        </table>

        <h3>Development Dependencies</h3>
        <table>
            <thead><tr><th>Package</th><th>Version</th><th>Purpose</th></tr></thead>
            <tbody>
    """
    
    for name, version in sorted(dev_deps.items()):
        html_content += f"<tr><td><strong>{name}</strong></td><td><span class='badge'>{version}</span></td><td>Development Tool</td></tr>"

    html_content += f"""
            </tbody>
        </table>
        
        <div class="footer" style="margin-top: 50px; text-align: center; color: #94a3b8; font-size: 0.9em;">
            <p>Generated automatically by Antigravity Agent for IRIS1 Project.</p>
        </div>
    </body>
    </html>
    """
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write(html_content)
    
    print(f"Report generated at: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_report()
