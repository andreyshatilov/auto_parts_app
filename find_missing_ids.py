import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    with open('index_working.html', 'r', encoding='utf-16-le') as f:
        old_html = f.read()
except:
    with open('index_working.html', 'r', encoding='utf-8') as f:
        old_html = f.read()

for id_name in ['userNameDisplay', 'userPhoneDisplay', 'userAvatar']:
    lines = old_html.split('\n')
    for i, line in enumerate(lines):
        if f'id="{id_name}"' in line:
            start = max(0, i - 3)
            end = min(len(lines), i + 4)
            print(f'\n=== {id_name} (line {i+1}) ===')
            for j in range(start, end):
                marker = '>>>' if j == i else '   '
                print(f'{marker} {j+1}: {lines[j]}')
