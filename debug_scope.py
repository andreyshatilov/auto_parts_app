with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Find setupEventListeners scope
idx = js.find('function setupEventListeners()')
brace = 0
end_setup = -1
for i in range(idx, len(js)):
    if js[i] == '{': brace += 1
    elif js[i] == '}': brace -= 1
    if brace == 0 and i > idx:
        end_setup = i
        break

setup_body = js[idx:end_setup]
if 'renderGarage' in setup_body:
    print('renderGarage IS referenced inside setupEventListeners!')
else:
    print('renderGarage NOT inside setupEventListeners')

# Check if renderGarage is defined AFTER setupEventListeners ends
rg_pos = js.find('function renderGarage(')
print(f'setupEventListeners ends at position: {end_setup}')
print(f'renderGarage defined at position: {rg_pos}')

# The real fix: make renderGarage a regular function (not async) or use window.renderGarage
# Actually check - is renderGarage called from showMainScreen which is BEFORE its definition?
sm_pos = js.find('function showMainScreen(')
print(f'showMainScreen defined at position: {sm_pos}')

# Check if there's a duplicate renderGarage inside setupEventListeners
lines = setup_body.split('\n')
for i, line in enumerate(lines):
    if 'renderGarage' in line:
        print(f'  setupEventListeners line {i}: {line.strip()[:100]}')

# Check editProfileForm close modal
if 'closeEditProfileModal' in js:
    print('closeEditProfileModal exists')
else:
    print('closeEditProfileModal MISSING')

# Find editProfileForm submit handler
for i, line in enumerate(js.split('\n')):
    if 'editProfileForm' in line and 'submit' in line:
        print(f'editProfileForm submit at line {i+1}: {line.strip()[:100]}')
