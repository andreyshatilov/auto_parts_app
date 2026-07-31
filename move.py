import io

with io.open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

garage_end_idx = -1
for i, line in enumerate(lines):
    if '<!-- Екран 2: Запчастини та Швидкий підбір -->' in line:
        garage_end_idx = i
        break

timeline_start = -1
timeline_end = -1
for i in range(garage_end_idx):
    if '<!-- Хронологія Сервісної Книжки -->' in lines[i]:
        timeline_start = i
        break

if timeline_start != -1:
    for i in range(timeline_start, garage_end_idx):
        if '</section>' in lines[i]:
            timeline_end = i + 1
            break

catalog_start = -1
catalog_end = -1
for i in range(garage_end_idx):
    if '<!-- Каталог вузлів -->' in lines[i] or 'Вузли та Компоненти Авто' in lines[i]:
        catalog_start = i - 1 if '<!--' in lines[i-1] else i
        break

if catalog_start != -1:
    for i in range(catalog_start, garage_end_idx):
        if '<button class="btn btn-secondary" onclick="openAddNewCarModal()"' in lines[i] or '<!-- Кнопка додавання авто' in lines[i]:
            catalog_end = i - 1 if '<!--' in lines[i-1] else i
            break

print(f"Timeline: {timeline_start} to {timeline_end}")
print(f"Catalog: {catalog_start} to {catalog_end}")

if timeline_start != -1 and catalog_start != -1:
    # They are likely contiguous. Let's find the absolute min and max of these two blocks.
    extract_start = min(timeline_start, catalog_start)
    extract_end = max(timeline_end, catalog_end)
    
    extracted = lines[extract_start:extract_end]
    del lines[extract_start:extract_end]
    
    # Find insertion point
    insert_idx = -1
    for i, line in enumerate(lines):
        if 'id="viewRequests"' in line:
            for j in range(i, len(lines)):
                if 'id="requestForm"' in lines[j]:
                    for k in range(j, len(lines)):
                        if '</form>' in lines[k]:
                            insert_idx = k + 3
                            break
                    break
            break
            
    if insert_idx != -1:
        lines = lines[:insert_idx] + extracted + lines[insert_idx:]
        with io.open('client_frontend/index.html', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Moved successfully!")
    else:
        print("Could not find insert index.")
else:
    print("Could not extract blocks.")
