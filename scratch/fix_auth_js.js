const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '../client_frontend/app.js');
let js = fs.readFileSync(filePath, 'utf-8');

const regex = /registerForm\.addEventListener\('submit', async \(e\) => \{[\s\S]*?loginForm\.addEventListener\('submit', async \(e\) => \{[\s\S]*?showMainScreen\(currentClient\);\s*\} catch \(err\) \{\s*showToast\(` \$\{err\.message\}`, 'error'\);\s*\}\s*\}\);/m;

const replacement = `let currentRegEmail = '';

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fName = document.getElementById('regFirstName').value.trim();
        const lName = document.getElementById('regLastName').value.trim();
        const phone = document.getElementById('regPhone').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value.trim();
        const hasMsgr = document.getElementById('regHasMessenger').checked;
        
        if (password.length < 6) return showToast('Пароль має містити мінімум 6 символів', 'error');

        try {
            const res = await fetch(\`\${API_BASE_URL}/auth/register\`, {
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
            showToast(\`\${err.message}\`, 'error');
        }
    });

    window.verifyOtp = async function() {
        const code = document.getElementById('otpCodeInput').value.trim();
        if(!code) return;
        try {
            const res = await fetch(\`\${API_BASE_URL}/auth/verify\`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: currentRegEmail, code: code })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка OTP');
            
            localStorage.setItem(TOKEN_STORAGE_KEY, data.auth_token);
            hideModal(document.getElementById('otpModal'));
            showToast('Email підтверджено! Акаунт активовано.', 'success');
            await fetchProfile(data.auth_token);
        } catch (err) {
            showToast(\`\${err.message}\`, 'error');
        }
    };

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const phoneOrEmail = document.getElementById('loginPhone').value.trim();
        const password = document.getElementById('loginPassword').value.trim();
        try {
            const res = await fetch(\`\${API_BASE_URL}/auth/login\`, {
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
            showToast(\`\${err.message}\`, 'error');
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
            const res = await fetch(\`\${API_BASE_URL}/auth/forgot-password\`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка');
            
            currentResetEmail = email;
            hideModal(document.getElementById('forgotPasswordModal'));
            showModal(document.getElementById('resetPasswordModal'));
            showToast('Код відновлення відправлено!', 'info');
        } catch (err) {
            showToast(\`\${err.message}\`, 'error');
        }
    };
    window.submitResetPassword = async function() {
        const code = document.getElementById('resetCodeInput').value.trim();
        const newPassword = document.getElementById('resetNewPasswordInput').value.trim();
        if(!code || newPassword.length < 6) return showToast('Заповніть всі поля (пароль мін 6 симв)', 'error');
        try {
            const res = await fetch(\`\${API_BASE_URL}/auth/reset-password\`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: currentResetEmail, code: code, new_password: newPassword })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка зміни пароля');
            
            hideModal(document.getElementById('resetPasswordModal'));
            showToast('Пароль успішно змінено! Увійдіть з новим паролем.', 'success');
            document.getElementById('loginPhone').value = currentResetEmail;
            document.getElementById('loginPassword').value = '';
        } catch (err) {
            showToast(\`\${err.message}\`, 'error');
        }
    };`;

js = js.replace(regex, replacement);
fs.writeFileSync(filePath, js, 'utf-8');
console.log('Successfully updated app.js!');
