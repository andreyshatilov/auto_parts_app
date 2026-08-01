import io

with io.open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

def check(t):
    return html.count(f'<{t}') - html.count(f'</{t}>')

print(f"div balance: {check('div')}")
print(f"section balance: {check('section')}")
print(f"form balance: {check('form')}")
