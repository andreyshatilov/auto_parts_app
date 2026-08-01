import io
import re

with io.open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

declarations = re.findall(r'const\s+(\w+)\s*=\s*document\.getElementById\([\'\"](\w+)[\'\"]\)', js)

with io.open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

for var, id in declarations:
    if f'"{id}"' not in html and f"'{id}'" not in html:
        print(f'MISSING ID in HTML: {id} (used by var {var})')
