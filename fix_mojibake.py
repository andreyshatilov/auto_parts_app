import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix Mojibake mapping
replacements = {
    '╨┤╨╛╨┤╨░╨╜╨╛ ╤Г ╨▓╨░╤И ╨У╨░╤А╨░╨╢!': 'додано у ваш Гараж!',
    '╨Ч ╨┐╨╛╨▓╨╡╤А╨╜╨╡╨╜╨╜╤П╨╝': 'З поверненням',
    '╨Ы╨░╤Б╨║╨░╨▓╨╛ ╨┐╤А╨╛╤Б╨╕╨╝╨╛': 'Ласкаво просимо',
    '╨░╨▓╤В╨╛': 'авто',
    '╨б╨┐╨╛╤З╨░╤В╨║╤Г ╨┤╨╛╨┤╨░╨╣╤В╨╡ ╨░╨▓╤В╨╛ ╨▓ ╨│╨░╤А╨░╨╢': 'Спочатку додайте авто в гараж',
    '╨Т╨░╤И ╨│╨░╤А╨░╨╢ ╨┐╨╛╤А╨╛╨╢╨╜╤Ц╨╣. ╨Ф╨╛╨┤╨░╨╣╤В╨╡ ╨┐╨╡╤А╤И╨╡ ╨░╨▓╤В╨╛ ╨╜╨╕╨╢╤З╨╡ (╨┤╨╛ 10 ╨╝╨░╤И╨╕╨╜).': 'Ваш гараж порожній. Додайте перше авто нижче (до 10 машин).',
    '╨Ф╨╛╨┤╨░╤В╨╕ VIN-╨║╨╛╨┤': 'Додати VIN-код',
    '╨Ф╨╛╨┤╨░╨╜╨╛ ╨▒╨╡╨╢ VIN': 'Додано без VIN'
}

for k, v in replacements.items():
    js = js.replace(k, v)

# Ensure closeEditProfileModal() is called in the profile submit handler
# Look for "Профіль оновлено" or similar if the previous script didn't apply properly
if 'closeEditProfileModal();' not in js:
    js = js.replace("showToast('Профіль успішно оновлено!');", "closeEditProfileModal();\n            showToast('Профіль успішно оновлено!');")
    js = js.replace("showToast('Профіль оновлено", "closeEditProfileModal();\n            showToast('Профіль оновлено")

# Fix renderGarage scoping by making sure it's exported to window object or defined globally
# The easiest way is to add window.renderGarage = renderGarage; right after it is defined,
# AND attach it in the file. But a better way is `window.renderGarage = function renderGarage...`
js = js.replace('function renderGarage(cars) {', 'window.renderGarage = function renderGarage(cars) {')
# Also attach showModal / hideModal to window just in case
js = js.replace('function showModal(modalEl) {', 'window.showModal = function showModal(modalEl) {')
js = js.replace('function hideModal(modalEl) {', 'window.hideModal = function hideModal(modalEl) {')

# Wait, if there are multiple declarations of renderGarage (e.g. one inside setupEventListeners), it could cause issues.
# Let's remove the second one if it exists.
# We'll just assign window.renderGarage globally at the end of the file.
js += '\n\nwindow.renderGarage = renderGarage;\nwindow.showModal = showModal;\nwindow.hideModal = hideModal;\n'

with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
# Bump cache version
html = html.replace('v=22.0', 'v=23.0')
with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
