import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Let's inspect line by line or section around addGarageCarForm
lines = js.split('\n')
for i, line in enumerate(lines[:60]):
    print(f"{i+1}: {line}")
