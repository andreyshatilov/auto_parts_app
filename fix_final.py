import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# FIX 1: renderGarage is async function - not hoisted. Change to regular function
js = js.replace('async function renderGarage(cars) {', 'function renderGarage(cars) {')
print('FIX 1: Changed renderGarage from async to regular function')

# FIX 2: Find editProfileForm submit handler and add closeEditProfileModal()
# Find the edit profile submit success block
lines = js.split('\n')
for i, line in enumerate(lines):
    if 'editProfileForm' in line:
        print(f'  Line {i+1}: {line.strip()[:100]}')

# Search for the success toast in edit profile handler  
edit_success_pattern = "showToast(' Профіль оновлено"
if edit_success_pattern in js:
    js = js.replace(edit_success_pattern, "closeEditProfileModal();\n            " + edit_success_pattern)
    print('FIX 2: Added closeEditProfileModal() after profile save')
else:
    # Try alternate pattern
    for i, line in enumerate(lines):
        if 'оновлено' in line.lower() or 'Профіль' in line and 'Toast' in line:
            print(f'  Toast line {i+1}: {line.strip()[:100]}')

# FIX 3: Fix encoding in showMainScreen welcome message
# Find "З поверненням" line
for i, line in enumerate(lines):
    if 'поверненням' in line or 'showToast' in line and 'first_name' in line:
        print(f'  Welcome line {i+1}: {line.strip()[:120]}')

with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

# Bump version
with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace('v=21.0', 'v=22.0')
with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Bumped to v=22.0')
