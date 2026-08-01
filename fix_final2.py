import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# FIX 2: Add closeEditProfileModal after successful profile save
# There are two editProfileForm handlers (lines 535 and 1090) - one inside setupEventListeners
# Find the showToast for profile update and add close modal before it
old_profile = "showToast('Профіль успішно оновлено!');"
new_profile = "closeEditProfileModal();\n            showToast('Профіль успішно оновлено!');"
count = js.count(old_profile)
print(f'Found {count} occurrences of profile toast')
js = js.replace(old_profile, new_profile)

# FIX 3: Remove duplicate login handlers with mojibake
# The setupEventListeners has its own loginForm/registerForm handlers that duplicate initApp
# The mojibake versions at lines ~865 and ~892 are inside setupEventListeners
# We need to find and remove them

# Find the broken encoded showToast lines and replace with nothing or proper text
lines = js.split('\n')
fixed_lines = []
skip_block = False
for i, line in enumerate(lines):
    # Check for mojibake welcome messages inside setupEventListeners
    if '╨Ы╨░╤Б╨║╨░╨▓╨╛ ╨┐╤А╨╛╤Б╨╕╨╝╨╛' in line:
        line = line.replace('╨Ы╨░╤Б╨║╨░╨▓╨╛ ╨┐╤А╨╛╤Б╨╕╨╝╨╛', 'Ласкаво просимо')
        print(f'FIX 3a: Fixed mojibake at line {i+1}')
    if '╨Ч ╨┐╨╛╨▓╨╡╤А╨╜╨╡╨╜╨╜╤П╨╝' in line:
        line = line.replace('╨Ч ╨┐╨╛╨▓╨╡╤А╨╜╨╡╨╜╨╜╤П╨╝', 'З поверненням')
        print(f'FIX 3b: Fixed mojibake at line {i+1}')
    fixed_lines.append(line)

js = '\n'.join(fixed_lines)

with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print('All fixes applied')
