with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_html = """<label for="clientVinInput">VIN-код (17 символів, обов'язково)</label>
                    <div class="vin-input-wrapper">
                        <input type="text" id="clientVinInput" placeholder="17 символів (бажано для автопідбору)">
                        <span class="vin-counter" id="clientVinCounter">0/17</span>
                    </div>"""

new_html = """<label for="clientVinInput">VIN-код (17 символів)</label>
                    <div class="vin-input-wrapper">
                        <input type="text" id="clientVinInput" placeholder="17 символів (бажано для автопідбору)">
                        <span class="vin-counter" id="clientVinCounter">0/17</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                        <input type="checkbox" id="noVinCheckbox" style="width: 16px; height: 16px;">
                        <label for="noVinCheckbox" style="font-size: 13px; font-weight: normal; color: var(--text-muted); margin: 0;">Не знаю VIN-код / Додам пізніше</label>
                    </div>"""

if old_html in html:
    html = html.replace(old_html, new_html)
    with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('HTML replaced!')
else:
    print('HTML not found!')
