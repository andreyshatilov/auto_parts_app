import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('client_frontend/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

import re
for m in re.finditer(r'\.auth-form|\.tab-btn', css):
    start = m.start()
    print(css[start:start+250])
    print('---')
