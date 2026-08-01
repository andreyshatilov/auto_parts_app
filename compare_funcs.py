import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('app_working.js', 'r', encoding='utf-16-le') as f:
    old_js = f.read()

with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    new_js = f.read()

old_funcs = set(re.findall(r'function\s+(\w+)\s*\(', old_js))
new_funcs = set(re.findall(r'function\s+(\w+)\s*\(', new_js))

missing = old_funcs - new_funcs
extra = new_funcs - old_funcs

print(f'Old functions count: {len(old_funcs)}')
print(f'New functions count: {len(new_funcs)}')
print(f'\nMISSING in new (were in old): {len(missing)}')
for f in sorted(missing):
    print(f'  - {f}')

print(f'\nNEW in current (not in old): {len(extra)}')
for f in sorted(extra):
    print(f'  + {f}')
