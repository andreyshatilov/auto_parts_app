import io

with io.open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print('mainScreen count:', html.count('id="mainScreen"'))
print('authScreen count:', html.count('id="authScreen"'))
