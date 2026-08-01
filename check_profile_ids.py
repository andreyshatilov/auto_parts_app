import io

with io.open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

ids = ['profileFullName', 'profilePhone', 'profileEmail', 'profileShipping']
for i in ids:
    if f'"{i}"' not in html and f"'{i}'" not in html:
        print(f'{i} MISSING in HTML')
