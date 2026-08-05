import codecs

with codecs.open('client_frontend/app.js', 'r', 'utf-8') as f:
    content = f.read()

replacements = [
    ("clientVinInput.addEventListener", "if (clientVinInput) clientVinInput.addEventListener"),
    ("registerForm.addEventListener", "if (registerForm) registerForm.addEventListener"),
    ("loginForm.addEventListener", "if (loginForm) loginForm.addEventListener"),
    ("addGarageCarForm.addEventListener", "if (addGarageCarForm) addGarageCarForm.addEventListener"),
    ("requestForm.addEventListener", "if (requestForm) requestForm.addEventListener"),
    ("returnForm.addEventListener", "if (returnForm) returnForm.addEventListener"),
    ("chatSendForm.addEventListener", "if (chatSendForm) chatSendForm.addEventListener")
]

for old, new in replacements:
    if old in content and "if (" not in content[content.find(old)-10:content.find(old)]:
        content = content.replace(old, new)

with codecs.open('client_frontend/app.js', 'w', 'utf-8') as f:
    f.write(content)

print("All event listeners safely guarded!")
