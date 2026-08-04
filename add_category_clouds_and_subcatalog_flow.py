import re

# 1. Update client_frontend/index.html to add system category cards ("Облака вузлів") in viewRequests
with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add Category Cards grid inside viewRequests right below form
old_form_end = '''                                <button type="submit" class="btn btn-primary" style="font-size: 16px; padding: 14px; border-radius: 12px; font-weight: 800; margin-top: 6px;">
                                    <span>🚀 Надіслати запит експерту</span>
                                </button>
                            </form>
                        </div>
                    </section>
                </div><!-- End of viewRequests -->'''

new_form_end = '''                                <button type="submit" class="btn btn-primary" style="font-size: 16px; padding: 14px; border-radius: 12px; font-weight: 800; margin-top: 6px;">
                                    <span>🚀 Надіслати запит експерту</span>
                                </button>
                            </form>
                        </div>

                        <!-- 🛠️ ВУЗЛИ ТА КАТЕГОРІЇ АВТО (ОБЛАКА ВУЗЛІВ ДЛЯ ДЕТАЛЬНОГО ВИБОРУ) -->
                        <div style="margin-top: 20px;">
                            <div style="font-size: 15px; font-weight: 800; color: var(--text-main); margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                                <span>🛠️ Або оберіть деталь по категоріях:</span>
                            </div>

                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                                
                                <!-- 1. Двигун & Олива -->
                                <div class="card" style="padding: 12px; border-radius: 12px; cursor: pointer; background: #ffffff; border: 1px solid var(--border-color); transition: transform 0.2s;" onclick="openSubCatalog('engine')">
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <span style="font-size: 24px;">⚙️</span>
                                        <div>
                                            <div style="font-weight: 800; font-size: 13px; color: var(--text-main);">Двигун & Олива</div>
                                            <div style="font-size: 10px; color: var(--text-muted);">Масла, свічки, ГРМ</div>
                                        </div>
                                    </div>
                                </div>

                                <!-- 2. Гальмівна система -->
                                <div class="card" style="padding: 12px; border-radius: 12px; cursor: pointer; background: #ffffff; border: 1px solid var(--border-color); transition: transform 0.2s;" onclick="openSubCatalog('brakes')">
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <span style="font-size: 24px;">🛑</span>
                                        <div>
                                            <div style="font-weight: 800; font-size: 13px; color: var(--text-main);">Гальмівна система</div>
                                            <div style="font-size: 10px; color: var(--text-muted);">Диски, колодки, рідина</div>
                                        </div>
                                    </div>
                                </div>

                                <!-- 3. Ходова та Підвіска -->
                                <div class="card" style="padding: 12px; border-radius: 12px; cursor: pointer; background: #ffffff; border: 1px solid var(--border-color); transition: transform 0.2s;" onclick="openSubCatalog('suspension')">
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <span style="font-size: 24px;">🔩</span>
                                        <div>
                                            <div style="font-weight: 800; font-size: 13px; color: var(--text-main);">Ходова & Підвіска</div>
                                            <div style="font-size: 10px; color: var(--text-muted);">Амортизатори, важелі</div>
                                        </div>
                                    </div>
                                </div>

                                <!-- 4. Трансмісія & Зчеплення -->
                                <div class="card" style="padding: 12px; border-radius: 12px; cursor: pointer; background: #ffffff; border: 1px solid var(--border-color); transition: transform 0.2s;" onclick="openSubCatalog('transmission')">
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <span style="font-size: 24px;">⚙️</span>
                                        <div>
                                            <div style="font-weight: 800; font-size: 13px; color: var(--text-main);">Трансмісія & КПП</div>
                                            <div style="font-size: 10px; color: var(--text-muted);">Мастило КПП, зчеплення</div>
                                        </div>
                                    </div>
                                </div>

                                <!-- 5. Електрика & Освітлення -->
                                <div class="card" style="padding: 12px; border-radius: 12px; cursor: pointer; background: #ffffff; border: 1px solid var(--border-color); transition: transform 0.2s;" onclick="openSubCatalog('electrical')">
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <span style="font-size: 24px;">⚡</span>
                                        <div>
                                            <div style="font-weight: 800; font-size: 13px; color: var(--text-main);">Електрика & Свет</div>
                                            <div style="font-size: 10px; color: var(--text-muted);">Акумулятори, лампи</div>
                                        </div>
                                    </div>
                                </div>

                                <!-- 6. Охолодження & Клімат -->
                                <div class="card" style="padding: 12px; border-radius: 12px; cursor: pointer; background: #ffffff; border: 1px solid var(--border-color); transition: transform 0.2s;" onclick="openSubCatalog('cooling')">
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <span style="font-size: 24px;">❄️</span>
                                        <div>
                                            <div style="font-weight: 800; font-size: 13px; color: var(--text-main);">Охолодження</div>
                                            <div style="font-size: 10px; color: var(--text-muted);">Помпи, радіатори</div>
                                        </div>
                                    </div>
                                </div>

                            </div>
                        </div>
                    </section>
                </div><!-- End of viewRequests -->'''

if old_form_end in html:
    html = html.replace(old_form_end, new_form_end)
    print("Added category clouds grid inside viewRequests")
else:
    print("WARNING: Could not find old_form_end in index.html")

with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update openSubCatalog and addPartFromSubCatalog in client_frontend/app.js
with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Update openSubCatalog to work even if currentDetailCarId is null (by checking requestCarSelect)
old_open_subcat = '''window.openSubCatalog = function(catKey) {
    if (!currentDetailCarId) return showToast('Спочатку оберіть авто в гаражі!', 'error');
    const cat = SUB_CATALOGS[catKey];'''

new_open_subcat = '''window.openSubCatalog = function(catKey) {
    const reqCarSelect = document.getElementById('requestCarSelect');
    if (!currentDetailCarId && (!reqCarSelect || !reqCarSelect.value)) {
        return showToast('Спочатку додайте або оберіть авто в гаражі!', 'error');
    }
    const cat = SUB_CATALOGS[catKey];'''

if old_open_subcat in app_js:
    app_js = app_js.replace(old_open_subcat, new_open_subcat)
    print("Updated openSubCatalog in app.js")

# Update addPartFromSubCatalog to switch to requests tab properly
old_add_part = "switchNavTab('request');"
new_add_part = "switchNavTab('requests');"
if old_add_part in app_js:
    app_js = app_js.replace(old_add_part, new_add_part)
    print("Fixed switchNavTab in addPartFromSubCatalog")

with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Category clouds and subcatalog flow completed successfully!")
