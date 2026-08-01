import io
import re

with io.open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

ids = ['loginForm', 'addGarageCarForm', 'returnForm', 'chatSendForm', 'requestForm', 'clientVinInput', 'registerForm', 'claimPinForm', 'editProfileForm']
for i in ids:
    if f'id="{i}"' in html or f"id='{i}'" in html:
        pass
    else:
        print(f'{i} MISSING')
