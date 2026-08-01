import io

with io.open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'id="authScreen"' in line:
        print('auth_start:', i)
    if 'id="mainScreen"' in line:
        print('main_start:', i)
