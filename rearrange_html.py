import io

with io.open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'VIN: WBA33AY05NFP12345' in line:
        lines[i] = line.replace('VIN: WBA33AY05NFP12345', 'VIN: ---')
    if '3G1BE6SM7JS652422' in line:
        lines[i] = line.replace('3G1BE6SM7JS652422', '17 символів')

with io.open('admin_frontend/index.html', 'r', encoding='utf-8') as f:
    admin_lines = f.readlines()
for i, line in enumerate(admin_lines):
    if '3G1BE6SM7JS652422' in line:
        admin_lines[i] = line.replace('3G1BE6SM7JS652422', '17 символів')
with io.open('admin_frontend/index.html', 'w', encoding='utf-8') as f:
    f.writelines(admin_lines)

# 2. Extract sections from viewGarage
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if '<!-- Каталог вузлів -->' in line or 'Вузли та Компоненти Авто' in line:
        if start_idx == -1:
            start_idx = i - 1 if '<!--' in lines[i-1] else i
    if '<button class="btn btn-secondary" onclick="openAddNewCarModal()"' in line or '<!-- Кнопка додавання авто' in line:
        if end_idx == -1 and i > start_idx and start_idx != -1:
            end_idx = i - 1 if '<!--' in lines[i-1] else i
            break

print(f'extract_start: {start_idx}')
print(f'extract_end: {end_idx}')

req_insert = -1
for i, line in enumerate(lines):
    if 'id="viewRequests"' in line:
        for j in range(i, len(lines)):
            if '</form>' in lines[j] and ('requestForm' in lines[j-20] or 'id="sendRequestBtn"' in lines[j-5]):
                req_insert = j + 3
                break
        break

print(f'req_insert: {req_insert}')

if start_idx != -1 and end_idx != -1 and req_insert != -1:
    extracted = lines[start_idx:end_idx]
    del lines[start_idx:end_idx]
    
    # After deleting, req_insert shifts!
    req_insert -= (end_idx - start_idx)
    
    lines = lines[:req_insert] + extracted + lines[req_insert:]
    
    with io.open('client_frontend/index.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully moved!")
else:
    print("Could not find required blocks.")
