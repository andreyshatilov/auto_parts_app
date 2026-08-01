import re
import io

with io.open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

ids = re.findall(r"document\.getElementById\(['\"](.*?)['\"]\)", js)

with io.open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

missing = []
for i in set(ids):
    if f'id="{i}"' not in html and f"id='{i}'" not in html:
        missing.append(i)

print('Missing IDs in HTML:', missing)
