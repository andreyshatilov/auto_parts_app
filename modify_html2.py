import re
with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(
    r'(<label for="clientVinInput">[^<]+<\/label>\s*<div class="vin-input-wrapper">.*?<\/div>)',
    r'\1\n                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">\n                        <input type="checkbox" id="noVinCheckbox" style="width: 16px; height: 16px;">\n                        <label for="noVinCheckbox" style="font-size: 13px; font-weight: normal; color: var(--text-muted); margin: 0;">Не знаю VIN-код / Додам пізніше</label>\n                    </div>',
    html,
    flags=re.DOTALL
)

with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
