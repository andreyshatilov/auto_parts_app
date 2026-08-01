import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Update index.html
with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the 3D showroom block in carDetailModal
old_html_block = r'<!-- 3D / 360(.*?)<div style="font-size:13px;'
new_html_block = r'''<!-- CAR PHOTO / LOGO AREA -->
            <div style="position:relative; background: #f8fafc; border-radius:14px; overflow:hidden; min-height:180px; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:16px; margin-bottom:16px; border:1px solid rgba(203,213,225,0.8);">
                <div id="carHeroPhotoContainer" style="width:100%; display:flex; flex-direction:column; align-items:center; gap: 12px;">
                    <img id="carHeroPhoto" src="" alt="Auto Photo" style="max-height:220px; width:100%; object-fit:cover; border-radius:8px; display:none;">
                    <div id="carLogoPlaceholder" style="display:flex; justify-content:center; align-items:center; opacity:0.3; transform:scale(2.5); margin: 20px 0;">
                        <!-- Logo will be injected here -->
                    </div>
                </div>

                <div style="margin-top:16px; display:flex; justify-content:center; width:100%;">
                    <button class="btn btn-secondary" style="font-size:12px; padding:8px 16px; display:flex; align-items:center; gap:6px;" onclick="document.getElementById('customCarPhotoUpload').click()">
                        📷 Додати/Змінити фото
                    </button>
                    <input type="file" id="customCarPhotoUpload" accept="image/*" style="display:none;" onchange="uploadCustomCarPhoto(this.files[0])">
                </div>
            </div>

            <!-- ДЕТАЛІ -->
            <div style="font-size:13px;'''
            
html = re.sub(old_html_block, new_html_block, html, flags=re.DOTALL)
html = re.sub(r'v=\d+\.\d+', 'v=28.0', html)

with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update app.js
with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Remove init3dCarCanvas
js = re.sub(r'function init3dCarCanvas.*?\}\n\}\n', '', js, flags=re.DOTALL)
# Remove saveCustomCarPhoto
js = re.sub(r'window\.saveCustomCarPhoto = async function\(\) \{.*?\n\};\n', '', js, flags=re.DOTALL)

# Update openCarDetailModal logic for images
old_open_modal = r"""    const heroImg = document\.getElementById\('carHeroPhoto'\);
    const canvasWrapper = document\.getElementById\('car3dCanvasWrapper'\);
    const customPhotoInput = document\.getElementById\('customPhotoUrlInput'\);

    if \(car\.custom_photo_url\) \{
        heroImg\.src = car\.custom_photo_url;
        heroImg\.style\.display = 'block';
        canvasWrapper\.style\.display = 'none';
    \} else \{
        heroImg\.style\.display = 'none';
        canvasWrapper\.style\.display = 'flex';
        setTimeout\(\(\) => init3dCarCanvas\(car\), 50\);
    \}"""
    
new_open_modal = r"""    const heroImg = document.getElementById('carHeroPhoto');
    const logoPlaceholder = document.getElementById('carLogoPlaceholder');
    
    if (car.custom_photo_url) {
        heroImg.src = car.custom_photo_url;
        heroImg.style.display = 'block';
        logoPlaceholder.style.display = 'none';
    } else {
        heroImg.style.display = 'none';
        logoPlaceholder.innerHTML = getBrandEmblem(car.brand);
        logoPlaceholder.style.display = 'flex';
    }"""
js = re.sub(old_open_modal, new_open_modal, js)

upload_logic = """
window.uploadCustomCarPhoto = async function(file) {
    if(!file || !currentDetailCarId) return;
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (typeof handleChatImageUpload === 'function') {
        handleChatImageUpload(file, async (url) => {
            try {
                const res = await fetch(`${API_BASE_URL}/cars/${currentDetailCarId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                    body: JSON.stringify({ custom_photo_url: url })
                });
                const updatedCar = await res.json();
                if(!res.ok) throw new Error(updatedCar.detail || 'Помилка оновлення фото авто');
                showToast('Фото авто успішно оновлено!', 'success');
                await refreshGarage(token);
                openCarDetailModal(currentDetailCarId);
            } catch(err) {
                showToast(err.message, 'error');
            }
        });
    } else {
        showToast('Система завантаження тимчасово недоступна.', 'error');
    }
};
"""
js += "\n" + upload_logic

with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Removed showroom and replaced with logo/photo upload.")
