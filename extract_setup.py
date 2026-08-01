import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('app_working.js', 'r', encoding='utf-16-le') as f:
    lines = f.readlines()

in_func = False
func_lines = []
brace_count = 0

for line in lines:
    if 'function setupEventListeners()' in line:
        in_func = True
    if in_func:
        func_lines.append(line)
        brace_count += line.count('{')
        brace_count -= line.count('}')
        if brace_count == 0 and len(func_lines) > 1:
            break

if func_lines:
    print(f'Found setupEventListeners: {len(func_lines)} lines')
    with open('setupEventListeners_extracted.js', 'w', encoding='utf-8') as f:
        f.write(''.join(func_lines))
else:
    print('Not found')
