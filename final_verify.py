import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Final verification: check all critical things
with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = []

# 1. No duplicate const declarations
import re
const_decls = re.findall(r'const (\w+) = document\.getElementById', js)
from collections import Counter
dupes = {k: v for k, v in Counter(const_decls).items() if v > 1}
if dupes:
    checks.append(f'❌ DUPLICATE const declarations: {dupes}')
else:
    checks.append('✅ No duplicate const declarations')

# 2. Key functions exist
for func in ['setupEventListeners', 'showModal', 'hideModal', 'showMainScreen', 'renderGarage', 
             'switchAuthTab', 'switchNavTab', 'initBrandAndModelSelects', 'initApp', 
             'loadMyRequests', 'loadMyOrders', 'refreshGarage']:
    if f'function {func}(' in js:
        checks.append(f'✅ function {func} exists')
    else:
        checks.append(f'❌ MISSING function {func}')

# 3. car_models.js is loaded
if 'car_models.js' in html:
    checks.append('✅ car_models.js is in index.html')
else:
    checks.append('❌ car_models.js NOT in index.html')

# 4. car_models.js is loaded BEFORE app.js
car_pos = html.find('car_models.js')
app_pos = html.find('app.js')
if car_pos < app_pos:
    checks.append('✅ car_models.js loaded before app.js')
else:
    checks.append('❌ car_models.js loaded AFTER app.js')

# 5. DOMContentLoaded has try/catch
if 'try { initBrandAndModelSelects' in js:
    checks.append('✅ initBrandAndModelSelects wrapped in try/catch')
else:
    checks.append('⚠️ initBrandAndModelSelects NOT wrapped in try/catch')

# 6. No syntax issues
# Check for \\n literal strings that should be newlines
if '\\n' in js and 'addGarageCarForm.reset();\\n' in js:
    checks.append('❌ Literal \\n found (string escape issue)')
else:
    checks.append('✅ No literal \\n issues')

# 7. Version cache bust
if 'v=21.0' in html:
    checks.append('✅ Cache busted to v=21.0')
else:
    checks.append('⚠️ Cache version not updated')

for c in checks:
    print(c)
