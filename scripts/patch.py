import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
target_file = BASE_DIR / "apps/logistics_wizard/logistics_wizard/public/js/smart_workflow_widget.bundle.js"

if target_file.exists():
    with open(target_file, "r") as f:
        code = f.read()
    code = re.sub(r'function load_leaflet\(callback\) \{.*?\n\s+function render_shipment_timeline', r'function render_shipment_timeline', code, flags=re.DOTALL)
    code = re.sub(r'load_leaflet\(function\(\) \{', r'// load_leaflet removed', code)
    code = re.sub(r'\}\); // load leaflet end', r'', code)
    with open(target_file, "w") as f:
        f.write(code)
    print(f"Patched: {target_file}")
else:
    print(f"File not found: {target_file}")
