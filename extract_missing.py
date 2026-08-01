import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('app_working.js', 'r', encoding='utf-16-le') as f:
    lines = f.readlines()

# Extract both missing functions
for func_name in ['setupEventListeners', 'showModal']:
    in_func = False
    func_lines = []
    brace_count = 0
    
    for line in lines:
        if f'function {func_name}(' in line and not in_func:
            in_func = True
        if in_func:
            func_lines.append(line)
            brace_count += line.count('{')
            brace_count -= line.count('}')
            if brace_count == 0 and len(func_lines) > 1:
                break
    
    if func_lines:
        with open(f'{func_name}_extracted.js', 'w', encoding='utf-8') as f:
            f.write(''.join(func_lines))
        print(f'Extracted {func_name}: {len(func_lines)} lines')
    else:
        print(f'NOT FOUND: {func_name}')
