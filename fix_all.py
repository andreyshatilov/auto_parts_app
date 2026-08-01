import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read the extracted functions
with open('setupEventListeners_extracted.js', 'r', encoding='utf-8') as f:
    setup_func = f.read()

with open('showModal_extracted.js', 'r', encoding='utf-8') as f:
    show_modal_func = f.read()

# Read current app.js
with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Check if showModal already exists
if 'function showModal(' not in js:
    # Insert showModal before function hideModal
    if 'function hideModal(' in js:
        js = js.replace('function hideModal(', show_modal_func + '\nfunction hideModal(')
        print('Inserted showModal before hideModal')
    else:
        # Insert before initBrandAndModelSelects
        js = js.replace('function initBrandAndModelSelects(', show_modal_func + '\nfunction initBrandAndModelSelects(')
        print('Inserted showModal before initBrandAndModelSelects')
else:
    print('showModal already exists')

# 2. Check if setupEventListeners already exists
if 'function setupEventListeners()' not in js:
    # Insert before initBrandAndModelSelects
    js = js.replace('function initBrandAndModelSelects(', setup_func + '\n\nfunction initBrandAndModelSelects(')
    print('Inserted setupEventListeners')
else:
    print('setupEventListeners already exists')

# 3. Wrap initBrandAndModelSelects call in try/catch
old_dcl = """document.addEventListener('DOMContentLoaded', () => {
    initBrandAndModelSelects();
    initApp();
    setupEventListeners();
});"""

new_dcl = """document.addEventListener('DOMContentLoaded', () => {
    try { initBrandAndModelSelects(); } catch(e) { console.warn('initBrandAndModelSelects error:', e); }
    initApp();
    try { setupEventListeners(); } catch(e) { console.warn('setupEventListeners error:', e); }
});"""

if old_dcl in js:
    js = js.replace(old_dcl, new_dcl)
    print('Wrapped DOMContentLoaded calls in try/catch')
else:
    print('DOMContentLoaded block not found for replacement (may already be wrapped)')

# Write back
with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print('app.js updated')

# 4. Add car_models.js script tag to index.html BEFORE app.js
with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

if 'car_models.js' not in html:
    html = html.replace(
        '<script src="app.js?v=20.0"></script>',
        '<script src="js/car_models.js"></script>\n    <script src="app.js?v=21.0"></script>'
    )
    print('Added car_models.js to index.html and bumped version to 21.0')
else:
    # Just bump version
    html = html.replace('v=20.0', 'v=21.0')
    print('car_models.js already in index.html, bumped version')

# Also bump in styles.css link if any
html = html.replace('styles.css?v=19.0', 'styles.css?v=21.0')
html = html.replace('styles.css?v=20.0', 'styles.css?v=21.0')

with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('index.html updated')
