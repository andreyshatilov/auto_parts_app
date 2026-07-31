import io

with io.open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = 111
end_idx = 360

req_insert = -1
for i, line in enumerate(lines):
    if 'id="viewRequests"' in line:
        for j in range(i, len(lines)):
            if '<section class="section">' in lines[j]:
                req_insert = j + 1
                break
        break

if req_insert != -1:
    extracted = lines[start_idx:end_idx]
    del lines[start_idx:end_idx]
    
    req_insert -= (end_idx - start_idx)
    
    lines = lines[:req_insert] + extracted + lines[req_insert:]
    with io.open('client_frontend/index.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print('Success')
