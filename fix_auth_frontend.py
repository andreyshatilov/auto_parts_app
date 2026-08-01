import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Update HTML ---
with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Register Form fields addition
old_reg_phone = r"""                    <div class="form-group">
                        <label for="regPhone">Номер телефону <span class="req">*</span></label>
                        <input type="tel" id="regPhone" placeholder="+380931234567" required>
                    </div>"""
new_reg_phone = r"""                    <div class="form-group">
                        <label for="regPhone">Номер телефону <span class="req">*</span></label>
                        <input type="tel" id="regPhone" placeholder="+380931234567" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="regEmail">Email <span class="req">*</span></label>
                        <input type="email" id="regEmail" placeholder="your@email.com" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="regPassword">Пароль <span class="req">*</span></label>
                        <input type="password" id="regPassword" placeholder="Мінімум 6 символів" required minlength="6">
                    </div>"""
html = html.replace(old_reg_phone, new_reg_phone)

# Login Form
old_login = r"""                <form id="loginForm" class="auth-form" autocomplete="off">
                    <div class="form-group">
                        <label for="loginPhone">Ваш номер телефону <span class="req">*</span></label>
                        <input type="tel" id="loginPhone" placeholder="+380931234567" required>
                    </div>

                    <button type="submit" class="btn btn-primary" id="loginSubmitBtn">
                        <span>Увійти в особистий кабінет</span>
                    </button>
                </form>"""
new_login = r"""                <form id="loginForm" class="auth-form" autocomplete="off">
                    <div class="form-group">
                        <label for="loginPhone">Ваш Email або номер телефону <span class="req">*</span></label>
                        <input type="text" id="loginPhone" placeholder="+380931234567 або email@.com" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="loginPassword">Пароль <span class="req">*</span></label>
                        <input type="password" id="loginPassword" placeholder="Ваш пароль" required>
                    </div>

                    <div style="text-align: right; margin-bottom: 16px;">
                        <a href="#" onclick="openForgotPasswordModal()" style="color:var(--primary); font-size:12px; font-weight:600; text-decoration:none;">Забули пароль?</a>
                    </div>

                    <button type="submit" class="btn btn-primary" id="loginSubmitBtn">
                        <span>Увійти в особистий кабінет</span>
                    </button>
                </form>"""
html = html.replace(old_login, new_login)

# Add Modals before closing body
modals = r"""
    <!-- OTP Модалка -->
    <div id="otpModal" class="modal-backdrop" style="display: none; align-items:center; justify-content:center; padding:16px; z-index:9999;">
        <div class="card modal-content" style="max-width: 400px; width: 100%; background: var(--bg-card); color: var(--text-main); border-radius: 16px; padding: 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <h2 style="font-size:18px; font-weight:800; margin:0;">Підтвердження Email</h2>
                <button onclick="hideModal(document.getElementById('otpModal'))" style="background:none; border:none; color:var(--text-main); font-size:20px;">✕</button>
            </div>
            <p style="font-size:13px; color:var(--text-muted); margin-bottom:16px;">Ми відправили 6-значний код на вашу пошту (або перевірте консоль під час розробки). Введіть його нижче.</p>
            <div class="form-group">
                <input type="text" id="otpCodeInput" placeholder="123456" style="letter-spacing:4px; font-size:20px; text-align:center; font-weight:700;">
            </div>
            <button class="btn btn-primary" onclick="verifyOtp()" style="margin-top:10px;">Підтвердити</button>
        </div>
    </div>

    <!-- Забули пароль Модалка -->
    <div id="forgotPasswordModal" class="modal-backdrop" style="display: none; align-items:center; justify-content:center; padding:16px; z-index:9999;">
        <div class="card modal-content" style="max-width: 400px; width: 100%; background: var(--bg-card); color: var(--text-main); border-radius: 16px; padding: 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <h2 style="font-size:18px; font-weight:800; margin:0;">Відновлення пароля</h2>
                <button onclick="hideModal(document.getElementById('forgotPasswordModal'))" style="background:none; border:none; color:var(--text-main); font-size:20px;">✕</button>
            </div>
            <p style="font-size:13px; color:var(--text-muted); margin-bottom:16px;">Введіть ваш Email, щоб отримати код відновлення.</p>
            <div class="form-group">
                <input type="email" id="forgotEmailInput" placeholder="your@email.com" required>
            </div>
            <button class="btn btn-primary" onclick="sendForgotPassword()" style="margin-top:10px;">Отримати код</button>
        </div>
    </div>

    <!-- Скидання пароля Модалка -->
    <div id="resetPasswordModal" class="modal-backdrop" style="display: none; align-items:center; justify-content:center; padding:16px; z-index:9999;">
        <div class="card modal-content" style="max-width: 400px; width: 100%; background: var(--bg-card); color: var(--text-main); border-radius: 16px; padding: 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <h2 style="font-size:18px; font-weight:800; margin:0;">Новий пароль</h2>
                <button onclick="hideModal(document.getElementById('resetPasswordModal'))" style="background:none; border:none; color:var(--text-main); font-size:20px;">✕</button>
            </div>
            <div class="form-group">
                <label>Код з Email</label>
                <input type="text" id="resetCodeInput" placeholder="123456" style="letter-spacing:2px; text-align:center;">
            </div>
            <div class="form-group">
                <label>Новий пароль</label>
                <input type="password" id="resetNewPasswordInput" placeholder="Мінімум 6 символів" required minlength="6">
            </div>
            <button class="btn btn-primary" onclick="submitResetPassword()" style="margin-top:10px;">Встановити пароль</button>
        </div>
    </div>
"""
if "otpModal" not in html:
    html = html.replace('<!-- Контейнер Toast -->', modals + '\n    <!-- Контейнер Toast -->')

html = re.sub(r'v=\d+\.\d+', 'v=29.0', html)

with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# --- Update JS ---
with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Register JS
old_reg_js = r"""    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fName = document.getElementById('regFirstName').value.trim();
        const lName = document.getElementById('regLastName').value.trim();
        const phone = document.getElementById('regPhone').value.trim();
        const hasMsgr = document.getElementById('regHasMessenger').checked;

        try {
            const res = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    first_name: fName,
                    last_name: lName,
                    phone: phone,
                    has_messenger: hasMsgr
                })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка реєстрації');

            localStorage.setItem(TOKEN_STORAGE_KEY, data.auth_token);
            showToast('Успішна реєстрація!', 'success');
            await fetchProfile(data.auth_token);
        } catch (err) {
            showToast(`Помилка: ${err.message}`, 'error');
        }
    });"""

new_reg_js = r"""    let currentRegEmail = '';

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fName = document.getElementById('regFirstName').value.trim();
        const lName = document.getElementById('regLastName').value.trim();
        const phone = document.getElementById('regPhone').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value.trim();
        const hasMsgr = document.getElementById('regHasMessenger').checked;
        
        if (password.length < 6) return showToast('Пароль має бути мінімум 6 символів', 'error');

        try {
            const res = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    first_name: fName,
                    last_name: lName,
                    phone: phone,
                    email: email,
                    password: password,
                    has_messenger: hasMsgr
                })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка реєстрації');

            currentRegEmail = email;
            showToast('OTP відправлено на пошту!', 'info');
            showModal(document.getElementById('otpModal'));
        } catch (err) {
            showToast(`${err.message}`, 'error');
        }
    });

    window.verifyOtp = async function() {
        const code = document.getElementById('otpCodeInput').value.trim();
        if(!code) return;
        try {
            const res = await fetch(`${API_BASE_URL}/auth/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: currentRegEmail, code: code })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Невірний код');
            
            localStorage.setItem(TOKEN_STORAGE_KEY, data.auth_token);
            hideModal(document.getElementById('otpModal'));
            showToast('Email підтверджено! Успішна реєстрація.', 'success');
            await fetchProfile(data.auth_token);
        } catch (err) {
            showToast(`${err.message}`, 'error');
        }
    };
"""
js = js.replace(old_reg_js, new_reg_js)

# Login JS
old_login_js = r"""    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const phone = document.getElementById('loginPhone').value.trim();
        try {
            const res = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка входу');

            localStorage.setItem(TOKEN_STORAGE_KEY, data.auth_token);
            showToast('Успішний вхід!', 'success');
            await fetchProfile(data.auth_token);
        } catch (err) {
            showToast(`Помилка: ${err.message}`, 'error');
        }
    });"""

new_login_js = r"""    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const phoneOrEmail = document.getElementById('loginPhone').value.trim();
        const password = document.getElementById('loginPassword').value.trim();
        try {
            const res = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone_or_email: phoneOrEmail, password: password })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка входу');

            localStorage.setItem(TOKEN_STORAGE_KEY, data.auth_token);
            showToast('Успішний вхід!', 'success');
            await fetchProfile(data.auth_token);
        } catch (err) {
            showToast(`Помилка: ${err.message}`, 'error');
        }
    });

    let currentResetEmail = '';
    window.openForgotPasswordModal = function() {
        showModal(document.getElementById('forgotPasswordModal'));
    };
    window.sendForgotPassword = async function() {
        const email = document.getElementById('forgotEmailInput').value.trim();
        if(!email) return;
        try {
            const res = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка запиту');
            
            currentResetEmail = email;
            hideModal(document.getElementById('forgotPasswordModal'));
            showModal(document.getElementById('resetPasswordModal'));
            showToast('Код відновлення відправлено!', 'info');
        } catch (err) {
            showToast(`${err.message}`, 'error');
        }
    };
    window.submitResetPassword = async function() {
        const code = document.getElementById('resetCodeInput').value.trim();
        const newPassword = document.getElementById('resetNewPasswordInput').value.trim();
        if(!code || newPassword.length < 6) return showToast('Заповніть код та пароль (мінімум 6 симв)', 'error');
        try {
            const res = await fetch(`${API_BASE_URL}/auth/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: currentResetEmail, code: code, new_password: newPassword })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка зміни пароля');
            
            hideModal(document.getElementById('resetPasswordModal'));
            showToast('Пароль успішно змінено! Тепер можна увійти.', 'success');
            document.getElementById('loginPhone').value = currentResetEmail;
            document.getElementById('loginPassword').value = '';
        } catch (err) {
            showToast(`${err.message}`, 'error');
        }
    };
"""
js = js.replace(old_login_js, new_login_js)

with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Frontend auth UI updated.")
