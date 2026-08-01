import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace onclicks in the 6 cards. We can find them by the cat-title that follows them.
# 1. Двигун & Олива
html = re.sub(
    r'<div class="card parts-cat-card" onclick="applyPreset\([^>]*\)(.*?)<div class="cat-title">Двигун & Олива</div>',
    r'<div class="card parts-cat-card" onclick="openSubCatalog(\'engine\')">\1<div class="cat-title">Двигун & Олива</div>',
    html, flags=re.DOTALL
)
# 2. Гальмівна система
html = re.sub(
    r'<div class="card parts-cat-card" onclick="applyPreset\([^>]*\)(.*?)<div class="cat-title">Гальмівна система</div>',
    r'<div class="card parts-cat-card" onclick="openSubCatalog(\'brakes\')">\1<div class="cat-title">Гальмівна система</div>',
    html, flags=re.DOTALL
)
# 3. Ходова & Підвіска
html = re.sub(
    r'<div class="card parts-cat-card" onclick="applyPreset\([^>]*\)(.*?)<div class="cat-title">Ходова & Підвіска</div>',
    r'<div class="card parts-cat-card" onclick="openSubCatalog(\'suspension\')">\1<div class="cat-title">Ходова & Підвіска</div>',
    html, flags=re.DOTALL
)
# 4. Електрика & Свічки
html = re.sub(
    r'<div class="card parts-cat-card" onclick="applyPreset\([^>]*\)(.*?)<div class="cat-title">Електрика & Свічки</div>',
    r'<div class="card parts-cat-card" onclick="openSubCatalog(\'electrical\')">\1<div class="cat-title">Електрика & Свічки</div>',
    html, flags=re.DOTALL
)
# 5. Охолодження & Клімат
html = re.sub(
    r'<div class="card parts-cat-card" onclick="applyPreset\([^>]*\)(.*?)<div class="cat-title">Охолодження & Клімат</div>',
    r'<div class="card parts-cat-card" onclick="openSubCatalog(\'cooling\')">\1<div class="cat-title">Охолодження & Клімат</div>',
    html, flags=re.DOTALL
)
# 6. Трансмісія & Зчеплення
html = re.sub(
    r'<div class="card parts-cat-card" onclick="applyPreset\([^>]*\)(.*?)<div class="cat-title">Трансмісія & Зчеплення</div>',
    r'<div class="card parts-cat-card" onclick="openSubCatalog(\'transmission\')">\1<div class="cat-title">Трансмісія & Зчеплення</div>',
    html, flags=re.DOTALL
)

# Insert SubCatalog Modal
sub_modal = r"""
    <!-- Deep Catalog Modal -->
    <div id="subCatalogModal" class="modal-backdrop" style="display: none; align-items:center; justify-content:center; padding:16px; z-index:9999;">
        <div class="card modal-content" style="max-width: 500px; width: 100%; background: var(--bg-card); color: var(--text-main); border-radius: 16px; padding: 20px; display:flex; flex-direction:column; max-height:80vh;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <h2 id="subCatalogTitle" style="font-size:18px; font-weight:800; margin:0;">Категорія</h2>
                <button onclick="hideModal(document.getElementById('subCatalogModal'))" style="background:none; border:none; color:var(--text-main); font-size:20px; cursor:pointer;">✕</button>
            </div>
            <div id="subCatalogList" style="overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:8px;">
                <!-- Items will be generated here -->
            </div>
        </div>
    </div>
"""
if "subCatalogModal" not in html:
    html = html.replace('<!-- Контейнер Toast -->', sub_modal + '\n    <!-- Контейнер Toast -->')

with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML sub-catalog updated.")
