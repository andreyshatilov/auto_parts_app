import io

with io.open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_timeline = -1
end_pin = -1
for i, line in enumerate(lines):
    if '<!-- Хронологія Сервісної Книжки -->' in line:
        start_timeline = i
    if '<button class="btn btn-secondary" onclick="openAddNewCarModal()"' in line or 'id="addCarGarageBtn"' in line:
        if start_timeline != -1:
            end_pin = i
            break

if start_timeline != -1 and end_pin != -1:
    extracted = lines[start_timeline:end_pin]
    del lines[start_timeline:end_pin]
    
    # Now find where to insert them in viewRequests
    insert_idx = -1
    for i, line in enumerate(lines):
        if '<!-- Екран 2: Запчастини та Швидкий підбір -->' in line or 'id="viewRequests"' in line:
            pass
            
    # Let's insert them right after the section with the requestForm
    for i, line in enumerate(lines):
        if '</section>' in line and 'id="sendRequestBtn"' in lines[i-15:i+5][-20:]:
            insert_idx = i + 1
            break
            
    if insert_idx != -1:
        lines = lines[:insert_idx] + extracted + lines[insert_idx:]
        with io.open('client_frontend/index.html', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print('Moved sections successfully!')
    else:
        print('Could not find insert index')
else:
    print('Could not find extract indices')
