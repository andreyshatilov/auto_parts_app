import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Fix app.js
with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix getBrandEmblem onerror
img_return_old = r'return `<img src="https://www.car-logos.org/wp-content/uploads/maker/\$\{imgName\}\.png" alt="\$\{b\}" style="width:100%; height:100%; object-fit:contain; border-radius:12px; max-width:48px; max-height:48px;" onerror="this\.outerHTML=\\\`\$\{fallbackHtml\}\\\`">`;'
img_return_new = r'''const fallbackHtmlSafe = fallbackHtml.replace(/"/g, '&quot;');
    return `<img src="https://www.car-logos.org/wp-content/uploads/maker/${imgName}.png" alt="${b}" style="width:100%; height:100%; object-fit:contain; border-radius:12px; max-width:48px; max-height:48px;" onerror="this.outerHTML='${fallbackHtmlSafe}'">`;'''
js = re.sub(img_return_old, img_return_new, js)

# Fix mojibake in renderGarage
replacements = {
    '╨б╨┐╨╛╤З╨░╤В╨║╤Г ╨┤╨╛╨┤╨░╨╣╤В╨╡ авто ╨▓ ╨│╨░╤А╨░╨╢': 'Спочатку додайте авто в гараж',
    '╨Т╨░╤И ╨│╨░╤А╨░╨╢ ╨┐╨╛╤А╨╛╨╢╨╜╤Ц╨╣. ╨Ф╨╛╨┤╨░╨╣╤В╨╡ ╨┐╨╡╤А╤И╨╡ авто ╨╜╨╕╨╢╤З╨╡ (╨┤╨╛ 10 ╨╝╨░╤И╨╕╨╜).': 'Ваш гараж порожній. Додайте перше авто нижче (до 10 машин).',
    '╨Э╨╡ ╨▓╨║╨░╨╖╨░╨╜╨╛ (╨а╨╡╨║╨╛╨╝╨╡╨╜╨┤╨╛╨▓╨░╨╜╨╛ ╨┤╨╛╨┤╨░╤В╨╕)': 'Не вказано (Рекомендовано додати)',
    'G20 (7-╨╝╨╡ ╨┐╨╛╨║╨╛╨╗╤Ц╨╜╨╜╤П)': 'G20 (7-ме покоління)',
    '(258 ╨║.╤Б.)': '(258 к.с.)',
    '╤А.╨▓.': 'р.в.',
    '╨Я╨Ю╨Ъ╨Ю╨Ы╨Ж╨Э╨Э╨п / ╨Ъ╨г╨Ч╨Ю╨Т': 'ПОКОЛІННЯ / КУЗОВ',
    '╨а╨Ж╨Ъ ╨Т╨Ш╨Я╨г╨б╨Ъ╨г': 'РІК ВИПУСКУ',
    '╨Ф╨Т╨Ш╨У╨г╨Э & ╨Я╨Ю╨в╨г╨Ц╨Э╨Ж╨б╨в╨м': 'ДВИГУН & ПОТУЖНІСТЬ',
    '╨в╨а╨Р╨Э╨б╨Ь╨Ж╨б╨Ж╨п': 'ТРАНСМІСІЯ',
    '╨Р╨Ъ╨Я╨Я': 'АКПП',
    '╨Т╨║╨░╨╢╤Ц╤В╤М VIN ╨┤╨╗╤П ╨С╨╛╤А╤В╨╢╤Г╤А╨╜╨░╨╗╤Г ╤В╨░ ╨в╨Ю': 'Вкажіть VIN для Бортжурналу та ТО',
    '╨Т╨║╨░╨╖╨░╤В╨╕ VIN': 'Вказати VIN',
    'ЁЯПОя╕П ╨Ю╨│╨╗╤П╨┤ & ╨Я╨░╤Б╨┐╨╛╤А╤В': '👁️ Огляд & Паспорт',
    'ЁЯФС PIN ╨┤╨╗╤П ╨┐╤А╨╛╨┤╨░╨╢╤Г': '🔑 PIN для продажу',
    '╨Т╨╕╨┤╨░╨╗╨╕╤В╨╕ ╨╖ ╨│╨░╤А╨░╨╢╨░': 'Видалити з гаража',
    'ЁЯЧСя╕П': '🗑️'
}
for k, v in replacements.items():
    js = js.replace(k, v)

# Move loadMyRequests and loadMyOrders to top
loadReqMatch = re.search(r'function loadMyRequests\([\s\S]*?\n\}', js)
loadOrdMatch = re.search(r'function loadMyOrders\([\s\S]*?\n\}', js)

if loadReqMatch:
    reqFunc = loadReqMatch.group(0).replace('function loadMyRequests', 'async function loadMyRequests')
    js = js.replace(loadReqMatch.group(0), '')
    js = reqFunc + '\n\n' + js
if loadOrdMatch:
    ordFunc = loadOrdMatch.group(0).replace('function loadMyOrders', 'async function loadMyOrders')
    js = js.replace(loadOrdMatch.group(0), '')
    js = ordFunc + '\n\n' + js

with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print('Updated app.js')

# 2. Fix styles.css (remove background from viewGarage)
with open('client_frontend/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

css = re.sub(r'#viewGarage \{[^}]*background:[^}]*\}', 
             '#viewGarage {\n    padding: 20px 0 100px 0;\n    min-height: 100vh;\n}', css)

with open('client_frontend/styles.css', 'w', encoding='utf-8') as f:
    f.write(css)
print('Updated styles.css')

# 3. Bump cache version
with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'v=\d+\.\d+', 'v=25.0', html)
with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Updated index.html')
