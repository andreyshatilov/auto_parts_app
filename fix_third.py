import io, sys
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Update styles.css for toast z-index
with open('client_frontend/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()
css = css.replace('z-index: 1000;', 'z-index: 99999;')
with open('client_frontend/styles.css', 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated styles.css z-index")

# 2. Update index.html for two shipping fields and bump cache version
with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_shipping_html = '''<div class="form-group">
                    <label for="editShipping">Адреса доставки Нової Пошти</label>
                    <input type="text" id="editShipping" placeholder="м. Київ, Відділення №1">
                </div>'''
                
new_shipping_html = '''<div class="form-group">
                    <label for="editShippingCity">Місто (Нова Пошта)</label>
                    <input type="text" id="editShippingCity" placeholder="Київ">
                </div>
                <div class="form-group">
                    <label for="editShippingBranch">Відділення Нової Пошти</label>
                    <input type="text" id="editShippingBranch" placeholder="№1">
                </div>'''

# Fallback pattern if the html differs
if old_shipping_html in html:
    html = html.replace(old_shipping_html, new_shipping_html)
else:
    # Use regex
    html = re.sub(
        r'<div class="form-group">\s*<label for="editShipping">.*?</label>\s*<input type="text" id="editShipping".*?>\s*</div>',
        new_shipping_html,
        html,
        flags=re.DOTALL
    )
    
html = html.replace('v=23.0', 'v=24.0')

with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated index.html")

# 3. Update app.js
with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix renderGarage hoisting
js = js.replace('window.renderGarage = function renderGarage(cars) {', 'function renderGarage(cars) {')

# Fix profile save logic to use two fields
# Find shipping value retrieval
old_shipping_js = "const shipping = document.getElementById('editShipping').value.trim();"
new_shipping_js = """const city = document.getElementById('editShippingCity').value.trim();
        const branch = document.getElementById('editShippingBranch').value.trim();
        let shipping = '';
        if (city || branch) {
            shipping = [city, branch].filter(Boolean).join(', Відділення ');
        }"""
        
# It might appear multiple times or inside setupEventListeners
js = js.replace(old_shipping_js, new_shipping_js)

# Also need to populate the fields when openEditProfileModal is called
old_populate = "document.getElementById('editShipping').value = currentClient.shipping_address || '';"
new_populate = """
    const shippingStr = currentClient.shipping_address || '';
    const parts = shippingStr.split(', Відділення ');
    document.getElementById('editShippingCity').value = parts[0] || '';
    document.getElementById('editShippingBranch').value = parts.length > 1 ? parts[1] : '';
"""
js = js.replace(old_populate, new_populate)


# Just in case, ensure editProfile modal is closed on success:
# Previously we tried to replace showToast('Профіль успішно оновлено!'), let's make sure it's closed in all handlers
# The handler is for 'editProfileForm'. Let's search for "if (editForm) {" inside setupEventListeners and make sure it calls closeEditProfileModal()
# We can do this safely using regex
if 'closeEditProfileModal();' not in js:
    print("Warning: closeEditProfileModal() still not in js, adding it.")
    js = js.replace("showToast('Профіль успішно оновлено!');", "closeEditProfileModal();\n            showToast('Профіль успішно оновлено!');")

with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated app.js")

