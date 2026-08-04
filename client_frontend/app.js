function applyPreset(text) {
    document.getElementById('requestText').value = text;
    switchNavTab('requests');
    showToast(' Категорію/компонент додано в форму запиту!');
    const reqForm = document.getElementById('requestForm');
    if (reqForm) reqForm.scrollIntoView({ behavior: 'smooth' });
}

async function loadMyOrders(token) {
    try {
        const res = await fetch(`${API_BASE_URL}/orders/my`, {
            headers: { 'X-Auth-Token': token }
        });
        if (!res.ok) return;
        const orders = await res.json();
        renderMyOrders(orders);
        renderServiceTimeline(orders);
    } catch (err) {
        console.error(err);
    }
}

async function loadMyRequests(token) {
    try {
        const res = await fetch(`${API_BASE_URL}/requests/my`, {
            headers: { 'X-Auth-Token': token }
        });
        if (!res.ok) return;
        const requests = await res.json();
        renderRequests(requests);
    } catch (err) {
        console.error(err);
    }
}

function renderGarage(cars) {
    garageCountBadge.textContent = `${cars.length}/10 авто`;
    if (cars.length > 0) {
        requestCarSelect.innerHTML = cars.map(c => `<option value="${c.id}">${escapeHtml(c.brand)} ${escapeHtml(c.model)} (VIN: ${escapeHtml(c.vin)})</option>`).join('');
    } else {
        requestCarSelect.innerHTML = `<option value="">Спочатку додайте авто в гараж</option>`;
    }

    const addCarBtn = document.querySelector('button[onclick="openAddNewCarModal()"]');
    if (addCarBtn) {
        if (cars.length > 0) {
            addCarBtn.style.border = 'none';
            addCarBtn.style.background = 'var(--primary)';
            addCarBtn.style.color = '#fff';
            addCarBtn.style.padding = '12px';
            addCarBtn.style.width = '100%';
            addCarBtn.style.marginTop = '20px';
            addCarBtn.innerHTML = '<span>+ Додати ще авто</span>';
        } else {
            addCarBtn.style.border = '2px dashed var(--primary)';
            addCarBtn.style.background = 'transparent';
            addCarBtn.style.color = 'var(--primary)';
            addCarBtn.style.padding = '16px';
            addCarBtn.style.width = '100%';
            addCarBtn.innerHTML = '<span>+ Додати авто</span>';
        }
    }

    if (cars.length === 0) {
        garageContainer.innerHTML = `
            <div style="text-align: center; color: var(--text-muted); padding: 32px 16px; background: var(--bg-card); border-radius: 16px; border: 1px solid var(--border-color); margin-top: 12px;">
                <div style="font-size: 42px; margin-bottom: 8px;">🚗</div>
                <div style="font-weight: 700; font-size: 16px; color: var(--text-main); margin-bottom: 4px;">У вас поки немає доданих авто</div>
                <div style="font-size: 13px; color: var(--text-muted);">Натисніть кнопку нижче, щоб додати автомобіль</div>
            </div>
        `;
        return;
    }

    garageContainer.innerHTML = cars.map(car => {
        const isNoVin = !car.vin || car.vin.startsWith('NOVIN-');
        const vinDisplay = isNoVin ? '<span style="color:#d97706; font-weight:600;">Не вказано (Рекомендовано додати)</span>' : escapeHtml(car.vin);

        const genDisplay = car.generation || (car.modification && car.modification.includes('G20') ? car.modification : 'G20 (7-ме покоління)');
        const engineDisplay = `${car.engine_code || '2.0L Turbo B48'} ${car.horse_power ? `(${car.horse_power})` : ' (258 к.с.)'}`;

        return `
        <div class="garage-card" style="cursor:pointer; transition:transform 0.2s;" onclick="openCarDetailModal(${car.id})">
            <div class="garage-header-flex">
                <div>
                    <div class="garage-card-title">${escapeHtml(car.brand)} ${escapeHtml(car.model)} ${car.release_date ? `<span style="font-size:13px; color:var(--primary); font-weight:600;">(${escapeHtml(car.release_date)} р.в.)</span>` : ''}</div>
                    <div class="garage-card-vin">VIN: ${vinDisplay}</div>
                </div>
                <div class="brand-emblem-badge">
                    ${getBrandEmblem(car.brand)}
                </div>
            </div>
            
            ${car.custom_photo_url ? `
                <div style="margin-top:10px; width:100%; height:130px; border-radius:10px; overflow:hidden;">
                    <img src="${escapeHtml(car.custom_photo_url)}" alt="${escapeHtml(car.brand)}" style="width:100%; height:100%; object-fit:cover;">
                </div>
            ` : ''}

            <div class="garage-details" style="margin-top:10px;">
                <div><span class="g-label">ПОКОЛІННЯ / КУЗОВ</span><div class="g-value">${escapeHtml(genDisplay)}</div></div>
                <div><span class="g-label">РІК ВИПУСКУ</span><div class="g-value">${escapeHtml(car.release_date || '2020')} р.в.</div></div>
                <div><span class="g-label">ДВИГУН & ПОТУЖНІСТЬ</span><div class="g-value">${escapeHtml(engineDisplay)}</div></div>
                <div><span class="g-label">ТРАНСМІСІЯ</span><div class="g-value">${escapeHtml(car.transmission_type || 'АКПП')} ${escapeHtml(car.transmission_code || '(ZF 8HP51)')}</div></div>
            </div>

            ${isNoVin ? `
                <div style="margin-top:10px; background:#fffbe6; border:1px solid #ffe58f; padding:8px 12px; border-radius:10px; font-size:12px; display:flex; justify-content:space-between; align-items:center; gap:6px;">
                    <span style="color:#d48806; font-weight:600;"> Вкажіть VIN для Бортжурналу та ТО</span>
                    <button class="btn btn-primary" style="width:auto; padding:4px 10px; font-size:11px; white-space:nowrap;" onclick="event.stopPropagation(); openVinRecommendationModal(${car.id}, '${escapeHtml(car.brand)} ${escapeHtml(car.model)}')"> Вказати VIN</button>
                </div>
            ` : ''}

            <div style="display:flex; gap:6px; margin-top:10px;" onclick="event.stopPropagation();">
                <button class="btn btn-secondary" style="font-size:11px; padding:8px; flex:1;" onclick="openCarDetailModal(${car.id})">
                    👁️ Огляд & Паспорт
                </button>
                <button class="btn btn-secondary" style="font-size:11px; padding:8px; flex:1;" onclick="generateTransferCode(${car.id}, '${escapeHtml(car.brand)} ${escapeHtml(car.model)}')">
                    🔑 PIN для продажу
                </button>
                <button class="btn btn-delete" style="font-size:11px; padding:8px; width:auto;" title="Видалити з гаража" onclick="deleteCarFromGarage(${car.id}, '${escapeHtml(car.brand)}', '${escapeHtml(car.model)}', '${escapeHtml(car.vin)}')">
                    🗑️
                </button>
            </div>
        </div>
    `}).join('');
}

/**
 * Client Mobile App Logic: Міністерство Запчастин (Українська версія)
 * 
 * Управляє Нижньою Навігацією, Сервісною Книжкою Авто,
 * Швидкими Комплектами ТО, Запитами, Замовленнями та Чатом.
 */


const API_BASE_URL = window.location.origin.includes(':8000') || window.location.origin.includes('5500')
    ? 'http://localhost:8000/api/v1'
    : '/api/v1';

const TOKEN_STORAGE_KEY = 'min_zapchasty_client_token';



/* ==========================================
 * 1. DOM ELEMENTS & GLOBAL STATE
 * ========================================== */
// DOM Елементи
const authScreen = document.getElementById('authScreen');
const mainScreen = document.getElementById('mainScreen');
const registerForm = document.getElementById('registerForm');
const loginForm = document.getElementById('loginForm');
const userNameDisplay = document.getElementById('userNameDisplay');
const userPhoneDisplay = document.getElementById('userPhoneDisplay');
const userShippingDisplay = document.getElementById('userShippingDisplay');
const userAvatar = document.getElementById('userAvatar');
const garageContainer = document.getElementById('garageContainer');
const garageCountBadge = document.getElementById('garageCountBadge');
const addGarageCarForm = document.getElementById('addGarageCarForm');
const clientVinInput = document.getElementById('clientVinInput');
const clientVinCounter = document.getElementById('clientVinCounter');
const requestCarSelect = document.getElementById('requestCarSelect');
const requestForm = document.getElementById('requestForm');
const claimPinForm = document.getElementById('claimPinForm');
const requestsHistoryContainer = document.getElementById('requestsHistoryContainer');
const myOrdersContainer = document.getElementById('myOrdersContainer');
const serviceTimelineContainer = document.getElementById('serviceTimelineContainer');
const toastContainer = document.getElementById('toastContainer');
const returnModal = document.getElementById('returnModal');
const returnForm = document.getElementById('returnForm');
const chatModal = document.getElementById('chatModal');
const chatSendForm = document.getElementById('chatSendForm');
const chatMessagesContainer = document.getElementById('chatMessagesContainer');

let currentClient = null;
let activeReturnOrderId = null;
let activeChatRequestId = null;


document.addEventListener('DOMContentLoaded', () => {
    try { initBrandAndModelSelects(); } catch(e) { console.warn('initBrandAndModelSelects error:', e); }
    initApp();
    try { setupEventListeners(); } catch(e) { console.warn('setupEventListeners error:', e); }
});

async function initApp() {
    const savedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (savedToken) {
        try {
            await fetchProfile(savedToken);
        } catch {
            localStorage.removeItem(TOKEN_STORAGE_KEY);
            showAuthScreen();
        }
    } else {
        showAuthScreen();
    }
}

async function fetchProfile(token) {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: { 'X-Auth-Token': token }
    });
    if (!res.ok) throw new Error();
    currentClient = await res.json();
    showMainScreen(currentClient);
}

/**
 * Switches the main navigation tabs in the client interface.
 * Hides all main views and displays the requested view.
 * @param {string} tabName - The ID of the view to display (e.g., 'viewGarage', 'viewRequests').
 */
function switchNavTab(tabName) {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view-content').forEach(v => v.style.display = 'none');

    if (tabName === 'garage') {
        document.querySelectorAll('.nav-item')[0].classList.add('active');
        document.getElementById('viewGarage').style.display = 'block';
    } else if (tabName === 'requests') {
        document.querySelectorAll('.nav-item')[1].classList.add('active');
        document.getElementById('viewRequests').style.display = 'block';
    } else if (tabName === 'orders') {
        document.querySelectorAll('.nav-item')[2].classList.add('active');
        document.getElementById('viewOrders').style.display = 'block';
    } else if (tabName === 'profile') {
        document.querySelectorAll('.nav-item')[3].classList.add('active');
        document.getElementById('viewProfile').style.display = 'block';
    }
}

/**
 * Switches between Login and Register tabs on the Authentication screen.
 * @param {string} tabName - 'login' or 'register'.
 */
function switchAuthTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    if (tabName === 'register') {
        document.getElementById('tabRegisterBtn').classList.add('active');
        registerForm.classList.add('active');
    } else {
        document.getElementById('tabLoginBtn').classList.add('active');
        loginForm.classList.add('active');
    }
}

/**
 * Initializes all global event listeners for the application.
 * Binds form submissions (login, register, add car, etc.) and global UI clicks.
 * @returns {void}
 */

/* ==========================================
 * 3. EVENT LISTENERS
 * ========================================== */
function showMainScreen(client) {
    currentClient = client;
    authScreen.classList.remove('active');
    mainScreen.classList.add('active');

    if (userNameDisplay) userNameDisplay.textContent = `${client.first_name} ${client.last_name}`;
    if (userPhoneDisplay) userPhoneDisplay.textContent = client.phone;
    if (userAvatar) userAvatar.textContent = client.first_name ? client.first_name[0].toUpperCase() : 'M';
    if (userShippingDisplay) userShippingDisplay.textContent = client.shipping_address || 'Не вказано';

    document.getElementById('profileFullName').textContent = `${client.first_name} ${client.last_name}`;
    document.getElementById('profilePhone').textContent = client.phone;
    document.getElementById('profileEmail').textContent = client.email || 'Не вказано';
    document.getElementById('profileShipping').textContent = client.shipping_address || 'Не вказано';

    renderGarage(client.cars || []);
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    loadMyRequests(token);
    loadMyOrders(token);
}

async function refreshGarage(token) {
    const res = await fetch(`${API_BASE_URL}/clients/me/cars`, {
        headers: { 'X-Auth-Token': token }
    });
    if (res.ok) {
        const cars = await res.json();
        renderGarage(cars);
    }
}

window.showModal = function showModal(modalEl) {
    if (!modalEl) return;
    modalEl.style.display = 'flex';
    requestAnimationFrame(() => {
        modalEl.classList.add('active');
    });
}

window.hideModal = function hideModal(modalEl) {
    if (!modalEl) return;
    modalEl.classList.remove('active');
    setTimeout(() => {
        if (!modalEl.classList.contains('active')) {
            modalEl.style.display = 'none';
        }
    }, 220);
}

window.openAddNewCarModal = function() {
    showModal(document.getElementById('addNewCarModal'));
};

window.closeAddNewCarModal = function() {
    hideModal(document.getElementById('addNewCarModal'));
};

window.openEditProfileModal = function() {
    if (!currentClient) return;
    document.getElementById('editFirstName').value = currentClient.first_name || '';
    document.getElementById('editLastName').value = currentClient.last_name || '';
    document.getElementById('editEmail').value = currentClient.email || '';
    
    const shippingStr = currentClient.shipping_address || '';
    const parts = shippingStr.split(', Відділення ');
    document.getElementById('editShippingCity').value = parts[0] || '';
    document.getElementById('editShippingBranch').value = parts.length > 1 ? parts[1] : '';

    showModal(document.getElementById('editProfileModal'));
};

window.closeEditProfileModal = function() {
    hideModal(document.getElementById('editProfileModal'));
};

function initYearSelect() {
    const yearSelect = document.getElementById('clientYearSelect');
    if (!yearSelect) return;
    yearSelect.innerHTML = '<option value="">Не вказано</option>';
    const currentYear = new Date().getFullYear() + 1;
    for (let y = currentYear; y >= 1970; y--) {
        const opt = document.createElement('option');
        opt.value = `${y}`;
        opt.textContent = `${y} рік`;
        yearSelect.appendChild(opt);
    }
}

let lastVinDecodeData = null;

function setupEventListeners() {
    let lastDecodedVin = '';
    clientVinInput.addEventListener('input', async (e) => {
        let val = e.target.value.replace(/\s+/g, '').toUpperCase();
        e.target.value = val;
        clientVinCounter.textContent = `${val.length}/17`;

        if (val.length === 17 && val !== lastDecodedVin) {
            lastDecodedVin = val;
            try {
                const res = await fetch(`${API_BASE_URL}/vin/decode?vin=${val}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.is_decoded && data.brand) {
                        const brandSelect = document.getElementById('clientBrandSelect');
                        const modelSelect = document.getElementById('clientModelSelect');

                        let rawBrand = (data.brand || '').trim();
                        let brandFound = null;

                        if (rawBrand) {
                            brandFound = Array.from(brandSelect.options).find(opt => opt.value.toUpperCase() === rawBrand.toUpperCase());
                            if (!brandFound) {
                                brandFound = Array.from(brandSelect.options).find(opt => 
                                    opt.value.toUpperCase().includes(rawBrand.toUpperCase()) || 
                                    rawBrand.toUpperCase().includes(opt.value.toUpperCase())
                                );
                            }
                        }

                        if (brandFound && brandFound.value !== '__custom__') {
                            brandSelect.value = brandFound.value;
                        } else {
                            brandSelect.value = '__custom__';
                        }
                        brandSelect.onchange();
                        if (brandSelect.value === '__custom__') {
                            document.getElementById('clientCustomBrandInput').value = rawBrand;
                        }

                        let rawModel = (data.model || '').trim();
                        if (rawModel) {
                            let modelFound = null;
                            const opts = Array.from(modelSelect.options).filter(o => o.value && o.value !== '__custom__');
                            
                            modelFound = opts.find(opt => opt.value.toUpperCase() === rawModel.toUpperCase());
                            if (!modelFound) {
                                modelFound = opts.find(opt => 
                                    rawModel.toUpperCase().includes(opt.value.toUpperCase()) || 
                                    opt.value.toUpperCase().includes(rawModel.toUpperCase())
                                );
                            }

                            if (modelFound) {
                                modelSelect.value = modelFound.value;
                                modelSelect.onchange();
                            } else {
                                modelSelect.value = '__custom__';
                                modelSelect.onchange();
                                document.getElementById('clientCustomModelInput').value = rawModel;
                            }
                        }

                        if (data.release_year) {
                            const yearSelect = document.getElementById('clientYearSelect');
                            if (yearSelect) yearSelect.value = data.release_year;
                        }

                        if (data.body_type) {
                            const bodySelect = document.getElementById('clientBodySelect');
                            if (bodySelect) bodySelect.value = data.body_type;
                        }

                        if (data.engine) {
                            document.getElementById('clientEngineInput').value = data.engine;
                        }

                        if (data.fuel) {
                            const fuelSelect = document.getElementById('clientFuelSelect');
                            if (fuelSelect) fuelSelect.value = data.fuel;
                        }

                        if (data.transmission) {
                            const transSelect = document.getElementById('clientTransInput');
                            if (transSelect) transSelect.value = data.transmission;
                        }

                        // Зберігаємо повні дані VIN-декодера для використання при створенні авто
                        lastVinDecodeData = data;

                        showToast(` ${data.brand} ${data.model || ''} ${data.release_year ? '(' + data.release_year + ')' : ''} розпізнано за VIN!`);
                    }
                }
            } catch (err) {
                console.error(err);
            }
        }
    });

    const addVinInputEl = document.getElementById('addVinInput');
    if (addVinInputEl) {
        let modalDecodedVin = '';
        addVinInputEl.addEventListener('input', async (e) => {
            let val = e.target.value.replace(/\s+/g, '').toUpperCase();
            e.target.value = val;
            document.getElementById('addVinCounter').textContent = `${val.length}/17`;

            if (val.length === 17 && val !== modalDecodedVin) {
                modalDecodedVin = val;
                try {
                    const res = await fetch(`${API_BASE_URL}/vin/decode?vin=${val}`);
                    if (res.ok) {
                        const data = await res.json();
                        if (data.is_decoded && data.brand) {
                            showToast(` ${data.brand} ${data.model || ''} (${data.release_year || ''}) ╤А╨╛╨╖╨┐╤Ц╨╖╨╜╨░╨╜╨╛ ╨╖╨░ VIN!`);
                        }
                    }
                } catch (err) {}
            }
        });
    }

    const addVinFormEl = document.getElementById('addVinForm');
    if (addVinFormEl) {
        addVinFormEl.addEventListener('submit', async (e) => {
            e.preventDefault();
            const carId = document.getElementById('addVinCarId').value;
            const newVin = document.getElementById('addVinInput').value.trim();
            const token = localStorage.getItem(TOKEN_STORAGE_KEY);

            if (newVin.length !== 17) {
                showToast(' VIN-╨║╨╛╨┤ ╨┐╨╛╨▓╨╕╨╜╨╡╨╜ ╨╝╤Ц╤Б╤В╨╕╤В╨╕ ╤А╨╛╨▓╨╜╨╛ 17 ╤Б╨╕╨╝╨▓╨╛╨╗╤Ц╨▓!', 'error');
                return;
            }

            try {
                const decodeRes = await fetch(`${API_BASE_URL}/vin/decode?vin=${newVin}`);
                let updatePayload = { vin: newVin };
                if (decodeRes.ok) {
                    const decoded = await decodeRes.json();
                    if (decoded.brand) updatePayload.brand = decoded.brand;
                    if (decoded.model) updatePayload.model = decoded.model;
                    if (decoded.release_year) updatePayload.release_date = decoded.release_year;
                    if (decoded.engine) updatePayload.engine_code = decoded.engine;
                    if (decoded.transmission) updatePayload.transmission_type = decoded.transmission;
                    if (decoded.generation) updatePayload.generation = decoded.generation;
                    if (decoded.body_type) updatePayload.body_type = decoded.body_type;
                    if (decoded.drive_type) updatePayload.drive_type = decoded.drive_type;
                    if (decoded.horse_power) updatePayload.horse_power = decoded.horse_power;
                    if (decoded.trim) updatePayload.modification = decoded.trim;
                    if (decoded.fuel) updatePayload.fuel_type = decoded.fuel;
                    // Завод збірки
                    const plantParts = [decoded.plant_city, decoded.plant_country].filter(Boolean);
                    if (plantParts.length > 0) updatePayload.assembly_plant = plantParts.join(', ');
                }

                const res = await fetch(`${API_BASE_URL}/cars/${carId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                    body: JSON.stringify(updatePayload)
                });
                const car = await res.json();
                if (!res.ok) throw new Error(car.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨╛╨╜╨╛╨▓╨╗╨╡╨╜╨╜╤П VIN');

                showToast(` VIN-╨║╨╛╨┤ ╨╖╨▒╨╡╤А╨╡╨╢╨╡╨╜╨╛! ╨Т╤Ц╨┤╨║╤А╨╕╤В╨╛ ╨┤╨╛╤Б╤В╤Г╨┐ ╨┤╨╛ ╨б╨╡╤А╨▓╤Ц╤Б╨╜╨╛╨│╨╛ ╨С╨╛╤А╤В╨╢╤Г╤А╨╜╨░╨╗╤Г ╤В╨░ ╨в╨Ю ╨┤╨╗╤П ${car.brand} ${car.model}!`);
                closeVinRecommendationModal();
                await refreshGarage(token);
            } catch (err) {
                showToast(` ${err.message}`, 'error');
            }
        });
    }

    let currentRegEmail = '';

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fName = document.getElementById('regFirstName').value.trim();
        const lName = document.getElementById('regLastName').value.trim();
        const phone = document.getElementById('regPhone').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value.trim();
        const confirmPassword = document.getElementById('regConfirmPassword').value.trim();
        const hasMsgr = document.getElementById('regHasMessenger').checked;
        
        if (password.length < 6) return showToast('Пароль має містити мінімум 6 символів', 'error');
        if (password !== confirmPassword) return showToast('Паролі не співпадають!', 'error');
        if (!/^[\x00-\x7F]+$/.test(password)) return showToast('Пароль повинен містити лише англійські літери (латиницю), цифри та спецсимволи!', 'error');

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
            if (!res.ok) {
                let errorMsg = 'Помилка реєстрації';
                try {
                    const data = await res.json();
                    if (Array.isArray(data.detail)) {
                        errorMsg = data.detail.map(d => d.msg || d.detail).join(', ');
                    } else if (data.detail) {
                        errorMsg = data.detail;
                    }
                } catch (e) {
                    errorMsg = `Сервер тимчасово недоступний (${res.status})`;
                }
                throw new Error(errorMsg);
            }
            const data = await res.json();

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
            if (!res.ok) {
                let errorMsg = 'Помилка OTP';
                try {
                    const data = await res.json();
                    errorMsg = data.detail || errorMsg;
                } catch (e) {
                    errorMsg = `Сервер тимчасово недоступний (${res.status})`;
                }
                throw new Error(errorMsg);
            }
            const data = await res.json();
            
            localStorage.setItem(TOKEN_STORAGE_KEY, data.auth_token);
            hideModal(document.getElementById('otpModal'));
            showToast('Email підтверджено! Акаунт активовано.', 'success');
            await fetchProfile(data.auth_token);
        } catch (err) {
            showToast(`${err.message}`, 'error');
        }
    };

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const phoneOrEmail = document.getElementById('loginPhone').value.trim();
        const password = document.getElementById('loginPassword').value.trim();
        try {
            const res = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone_or_email: phoneOrEmail, password: password })
            });
            if (!res.ok) {
                let errorMsg = 'Помилка входу';
                try {
                    const data = await res.json();
                    errorMsg = data.detail || errorMsg;
                } catch (e) {
                    errorMsg = `Сервер тимчасово недоступний (${res.status})`;
                }
                throw new Error(errorMsg);
            }
            const data = await res.json();

            localStorage.setItem(TOKEN_STORAGE_KEY, data.auth_token);
            showToast('Успішний вхід!', 'success');
            await fetchProfile(data.auth_token);
        } catch (err) {
            showToast(`${err.message}`, 'error');
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
            if (!res.ok) {
                let errorMsg = 'Помилка';
                try {
                    const data = await res.json();
                    errorMsg = data.detail || errorMsg;
                } catch (e) {
                    errorMsg = `Сервер тимчасово недоступний (${res.status})`;
                }
                throw new Error(errorMsg);
            }
            const data = await res.json();
            
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
        if(!code || newPassword.length < 6) return showToast('Заповніть всі поля (пароль мін 6 симв)', 'error');
        if (!/^[\x00-\x7F]+$/.test(newPassword)) return showToast('Пароль повинен містити лише англійські літери (латиницю), цифри та спецсимволи!', 'error');
        try {
            const res = await fetch(`${API_BASE_URL}/auth/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: currentResetEmail, code: code, new_password: newPassword })
            });
            if (!res.ok) {
                let errorMsg = 'Помилка зміни пароля';
                try {
                    const data = await res.json();
                    errorMsg = data.detail || errorMsg;
                } catch (e) {
                    errorMsg = `Сервер тимчасово недоступний (${res.status})`;
                }
                throw new Error(errorMsg);
            }
            const data = await res.json();
            
            hideModal(document.getElementById('resetPasswordModal'));
            showToast('Пароль успішно змінено! Увійдіть з новим паролем.', 'success');
            document.getElementById('loginPhone').value = currentResetEmail;
            document.getElementById('loginPassword').value = '';
        } catch (err) {
            showToast(`${err.message}`, 'error');
        }
    };

    claimPinForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const pinCode = document.getElementById('pinInput').value.trim();
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);
        try {
            const res = await fetch(`${API_BASE_URL}/transfers/claim`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify({ pin_code: pinCode })
            });
            const car = await res.json();
            if (!res.ok) throw new Error(car.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨┐╤А╨╕╨╣╨╛╨╝╤Г авто');

            showToast(` ╨Т╤Ц╤В╨░╤Ф╨╝╨╛! ╨Р╨▓╤В╨╛╨╝╨╛╨▒╤Ц╨╗╤М ${car.brand} ${car.model} ╤В╨░ ╨▓╤Б╤П ╨╣╨╛╨│╨╛ ╤Ц╤Б╤В╨╛╤А╤Ц╤П ╨┐╤А╨╕╨╣╨╜╤П╤В╤Ц ╤Г ╨▓╨░╤И ╨│╨░╤А╨░╨╢!`);
            document.getElementById('pinInput').value = '';
            await refreshGarage(token);
        } catch (err) {
            showToast(` ${err.message}`, 'error');
        }
    });

    addGarageCarForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);

        const selectedBrand = document.getElementById('clientBrandSelect').value;
        const selectedModel = document.getElementById('clientModelSelect').value;

        const finalBrand = (selectedBrand === '__custom__') 
            ? document.getElementById('clientCustomBrandInput').value.trim() 
            : selectedBrand;
            
        const finalModel = (selectedModel === '__custom__') 
            ? document.getElementById('clientCustomModelInput').value.trim() 
            : selectedModel;

        if (!finalBrand || !finalModel) {
            showToast(' ╨С╤Г╨┤╤М ╨╗╨░╤Б╨║╨░, ╨╛╨▒╨╡╤А╤Ц╤В╤М ╨░╨▒╨╛ ╨▓╨║╨░╨╢╤Ц╤В╤М ╨╝╨░╤А╨║╤Г ╤В╨░ ╨╝╨╛╨┤╨╡╨╗╤М авто!', 'error');
            return;
        }

        let vinValue = clientVinInput.value.trim().toUpperCase();
        if (!vinValue) {
            vinValue = 'NOVIN-' + Math.random().toString(36).substring(2, 11).toUpperCase();
        } else if (vinValue.length !== 17) {
            showToast(' VIN-╨║╨╛╨┤ ╨┐╨╛╨▓╨╕╨╜╨╡╨╜ ╨╝╤Ц╤Б╤В╨╕╤В╨╕ ╤А╨╛╨▓╨╜╨╛ 17 ╤Б╨╕╨╝╨▓╨╛╨╗╤Ц╨▓ (╨░╨▒╨╛ ╨╖╨░╨╗╨╕╤И╤В╨╡ ╨┐╨╛╤А╨╛╨╢╨╜╤Ц╨╝)!', 'error');
            return;
        } else if (/^\d+$/.test(vinValue)) {
            showToast(' VIN-╨║╨╛╨┤ ╨╜╨╡ ╨╝╨╛╨╢╨╡ ╤Б╨║╨╗╨░╨┤╨░╤В╨╕╤Б╤П ╨╗╨╕╤И╨╡ ╨╖ ╤Ж╨╕╤Д╤А! ╨Т╨▓╨╡╨┤╤Ц╤В╤М ╨╝╤Ц╨╢╨╜╨░╤А╨╛╨┤╨╜╨╕╨╣ VIN (╨╜╨░╨┐╤А., WBA33AY05NFP12345)', 'error');
            return;
        }

        const fuelVal = document.getElementById('clientFuelSelect')?.value || '';
        let engineVal = document.getElementById('clientEngineInput').value.trim();
        if (fuelVal) {
            engineVal = engineVal ? `${engineVal} (${fuelVal})` : fuelVal;
        }

        const bodyVal = document.getElementById('clientBodySelect')?.value || '';
        const genVal = document.getElementById('clientGenInput')?.value.trim() || '';
        const restyleVal = document.getElementById('clientRestyleSelect')?.value || '';

        const modParts = [];
        if (bodyVal) modParts.push(bodyVal);
        if (genVal) modParts.push(`╨Я╨╛╨║╨╛╨╗╤Ц╨╜╨╜╤П: ${genVal}`);
        if (restyleVal) modParts.push(restyleVal);
        const modificationStr = modParts.length > 0 ? modParts.join(' | ') : null;

        const mileageRaw = document.getElementById('clientMileageInput')?.value.trim();
        const mileageVal = mileageRaw ? parseInt(mileageRaw) : 120000;

        const carData = {
            vin: vinValue,
            brand: finalBrand,
            model: finalModel,
            modification: modificationStr,
            release_date: document.getElementById('clientYearSelect')?.value || null,
            engine_code: engineVal || null,
            transmission_type: document.getElementById('clientTransInput').value || null,
            mileage: mileageVal
        };

        // Додаємо дані з VIN-декодера (серія, привід, потужність, завод, тип кузова, паливо)
        if (lastVinDecodeData && lastVinDecodeData.is_decoded) {
            if (lastVinDecodeData.generation && !carData.generation) carData.generation = lastVinDecodeData.generation;
            if (lastVinDecodeData.body_type && !carData.body_type) carData.body_type = lastVinDecodeData.body_type;
            if (lastVinDecodeData.drive_type) carData.drive_type = lastVinDecodeData.drive_type;
            if (lastVinDecodeData.horse_power) carData.horse_power = lastVinDecodeData.horse_power;
            if (lastVinDecodeData.fuel) carData.fuel_type = lastVinDecodeData.fuel;
            if (lastVinDecodeData.trim && !carData.modification) carData.modification = lastVinDecodeData.trim;
            const plantParts = [lastVinDecodeData.plant_city, lastVinDecodeData.plant_country].filter(Boolean);
            if (plantParts.length > 0) carData.assembly_plant = plantParts.join(', ');
        }

        try {
            const res = await fetch(`${API_BASE_URL}/clients/me/cars`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify(carData)
            });
            const data = await res.json();
            if (!res.ok) {
                let errMsg = '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨┤╨╛╨┤╨░╨▓╨░╨╜╨╜╤П авто';
                if (typeof data.detail === 'string') errMsg = data.detail;
                else if (Array.isArray(data.detail)) errMsg = data.detail.map(d => d.msg || d.detail).join(', ');
                else if (data.detail && typeof data.detail === 'object') errMsg = JSON.stringify(data.detail);
                throw new Error(errMsg);
            }

            showToast(` ${data.brand} ${data.model} додано у ваш Гараж!`);
            addGarageCarForm.reset();
            initBrandAndModelSelects();
            clientVinCounter.textContent = '0/17';
            closeAddNewCarModal();
            await refreshGarage(token);

            if (vinValue.startsWith('NOVIN-')) {
                openVinRecommendationModal(data.id, `${data.brand} ${data.model}`);
            }
        } catch (err) {
            let errMsg = '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨┤╨╛╨┤╨░╨▓╨░╨╜╨╜╤П авто';
            if (typeof err === 'string') errMsg = err;
            else if (err && err.message && typeof err.message === 'string') errMsg = err.message;
            else if (err && typeof err === 'object') {
                try { errMsg = JSON.stringify(err); } catch(e) {}
            }
            showToast(` ${errMsg}`, 'error');
        }
    });

    requestForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);
        const carId = parseInt(requestCarSelect.value);
        const text = document.getElementById('requestText').value.trim();

        if (!carId) {
            showToast(' ╨Ю╨▒╨╡╤А╤Ц╤В╤М авто ╨╖ ╨│╨░╤А╨░╨╢╨░!', 'error');
            return;
        }

        try {
            const res = await fetch(`${API_BASE_URL}/requests/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify({ car_id: carId, client_message: text })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨╜╨░╨┤╤Б╨╕╨╗╨░╨╜╨╜╤П');

            showToast(' ╨Ч╨░╨┐╨╕╤В ╨╜╨░ ╨┐╤Ц╨┤╨▒╤Ц╤А ╨╜╨░╨┤╤Ц╤Б╨╗╨░╨╜╨╛ ╨╡╨║╤Б╨┐╨╡╤А╤В╤Г!');
            document.getElementById('requestText').value = '';
            await loadMyRequests(token);
        } catch (err) {
            showToast(` ${err.message}`, 'error');
        }
    });

    returnForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!activeReturnOrderId) return;
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);
        const reason = document.getElementById('returnReasonText').value.trim();

        try {
            const res = await fetch(`${API_BASE_URL}/returns/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify({ order_id: activeReturnOrderId, reason })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░');

            showToast(' ╨Ч╨░╤П╨▓╨║╨░ ╨╜╨░ ╨┐╨╛╨▓╨╡╤А╨╜╨╡╨╜╨╜╤П ╤В╨╛╨▓╨░╤А╤Г ╨╜╨░╨┤╤Ц╤Б╨╗╨░╨╜╨░!');
            closeReturnModal();
            await loadMyOrders(token);
        } catch (err) {
            showToast(` ${err.message}`, 'error');
        }
    });

    chatSendForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!activeChatRequestId) return;
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);
        const msg = document.getElementById('chatInput').value.trim();

        try {
            const res = await fetch(`${API_BASE_URL}/chat/messages?sender_type=client`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify({ request_id: activeChatRequestId, message: msg })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░');

            document.getElementById('chatInput').value = '';
            await loadChatMessages(activeChatRequestId);
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    const editForm = document.getElementById('editProfileForm');
    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = localStorage.getItem(TOKEN_STORAGE_KEY);
            const payload = {
                first_name: document.getElementById('editFirstName').value.trim(),
                last_name: document.getElementById('editLastName').value.trim(),
                email: document.getElementById('editEmail').value.trim() || null,
                shipping_address: document.getElementById('editShipping').value.trim() || null
            };
            try {
                const res = await fetch(`${API_BASE_URL}/clients/me`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                    body: JSON.stringify(payload)
                });
                const updatedClient = await res.json();
                if (!res.ok) throw new Error(updatedClient.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨╛╨╜╨╛╨▓╨╗╨╡╨╜╨╜╤П ╨┐╤А╨╛╤Д╤Ц╨╗╤О');

                currentClient = updatedClient;
                showMainScreen(currentClient);
                showToast('╨Я╤А╨╛╤Д╤Ц╨╗╤М ╤Г╤Б╨┐╤Ц╤И╨╜╨╛ ╨╛╨╜╨╛╨▓╨╗╨╡╨╜╨╛!');
                closeEditProfileModal();
            } catch (err) {
                showToast(err.message, 'error');
            }
        });
    }
}


function initBrandAndModelSelects() {
    initYearSelect();
    const brandSelect = document.getElementById('clientBrandSelect');
    const modelSelect = document.getElementById('clientModelSelect');
    const customRow = document.getElementById('customBrandModelRow');
    const customBrandGroup = document.getElementById('customBrandGroup');
    const customModelGroup = document.getElementById('customModelGroup');
    const customBrandInput = document.getElementById('clientCustomBrandInput');
    const customModelInput = document.getElementById('clientCustomModelInput');

    if (!brandSelect || !modelSelect) return;

    brandSelect.innerHTML = '<option value="">Оберіть марку...</option>';
    const sortedBrands = Object.keys(CAR_DATABASE).sort((a, b) => a.localeCompare(b, 'uk'));

    sortedBrands.forEach(brand => {
        const opt = document.createElement('option');
        opt.value = brand;
        opt.textContent = brand;
        brandSelect.appendChild(opt);
    });

    const otherBrandOpt = document.createElement('option');
    otherBrandOpt.value = '__custom__';
    otherBrandOpt.textContent = '+ Інша марка (вказати вручну)';
    brandSelect.appendChild(otherBrandOpt);

    function updateCustomFieldsVisibility() {
        const isCustomBrand = brandSelect.value === '__custom__';
        const isCustomModel = modelSelect.value === '__custom__';

        if (isCustomBrand) {
            customRow.style.display = 'flex';
            customBrandGroup.style.display = 'block';
            customBrandInput.required = true;
        } else {
            customBrandGroup.style.display = 'none';
            customBrandInput.required = false;
        }

        if (isCustomModel || isCustomBrand) {
            customRow.style.display = 'flex';
            customModelGroup.style.display = 'block';
            customModelInput.required = true;
        } else {
            customModelGroup.style.display = 'none';
            customModelInput.required = false;
        }

        if (!isCustomBrand && !isCustomModel) {
            customRow.style.display = 'none';
        }
    }

    brandSelect.onchange = () => {
        const selectedBrand = brandSelect.value;
        modelSelect.innerHTML = '';

        if (!selectedBrand) {
            modelSelect.disabled = true;
            modelSelect.innerHTML = '<option value="">Спочатку оберіть марку</option>';
            updateCustomFieldsVisibility();
            return;
        }

        modelSelect.disabled = false;

        if (selectedBrand === '__custom__') {
            const optCustom = document.createElement('option');
            optCustom.value = '__custom__';
            optCustom.textContent = '+ Інша модель (вказати вручну)';
            modelSelect.appendChild(optCustom);
            modelSelect.value = '__custom__';
        } else {
            const defaultOpt = document.createElement('option');
            defaultOpt.value = '';
            defaultOpt.textContent = 'Оберіть модель...';
            modelSelect.appendChild(defaultOpt);

            const models = CAR_DATABASE[selectedBrand] || [];
            models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m;
                modelSelect.appendChild(opt);
            });

            const optCustom = document.createElement('option');
            optCustom.value = '__custom__';
            optCustom.textContent = '+ Інша модель (вказати вручну)';
            modelSelect.appendChild(optCustom);
        }

        updateCustomFieldsVisibility();
    };

    modelSelect.onchange = () => {
        updateCustomFieldsVisibility();
    };
}

/**
 * Generates an HTML snippet for a car brand emblem.
 * Uses a public CDN (car-logos.org) for high-quality PNG logos.
 * Includes an 'onerror' fallback to display a text-based initial if the logo fails to load.
 * @param {string} brandName - The name of the car brand.
 * @returns {string} HTML string representing the emblem image or fallback.
 */
function getBrandEmblem(brandName) {
    if (!brandName) return '';
    const b = brandName.trim();
    let imgName = b.toLowerCase().replace(/ /g, '-');
    if (imgName === 'mercedes' || imgName === 'mercedes-benz') imgName = 'mercedes-benz';
    if (imgName === 'vw') imgName = 'volkswagen';
    if (imgName === 'alfa-romeo') imgName = 'alfa-romeo';
    if (imgName === 'chevrolet') imgName = 'chevrolet';
    if (imgName === 'land-rover') imgName = 'land-rover';
    
    // Fallback HTML if image fails to load
    const fallbackHtml = `<div style="display:flex;align-items:center;justify-content:center;width:48px;height:48px;border-radius:12px;background:#f1f5f9;color:#0f172a;font-weight:800;font-size:11px; text-align:center; overflow:hidden; border: 1px solid #e2e8f0; margin:auto;">${b.substring(0,5)}</div>`;
    
    const fallbackHtmlSafe = fallbackHtml.replace(/"/g, '&quot;');
    return `<img src="https://raw.githubusercontent.com/filippofilip95/car-logos-dataset/master/logos/thumb/${imgName}.png" alt="${b}" style="width:100%; height:100%; object-fit:contain; border-radius:12px; max-width:48px; max-height:48px;" onerror="this.outerHTML='${fallbackHtmlSafe}'">`;
}

function openVinRecommendationModal(carId, carName) {
    document.getElementById('addVinCarId').value = carId;
    document.getElementById('vinModalCarName').textContent = `Для автомобіля: ${carName}`;
    document.getElementById('addVinInput').value = '';
    document.getElementById('addVinCounter').textContent = '0/17';
    showModal(document.getElementById('vinRecommendationModal'));
}

function closeVinRecommendationModal() {
    hideModal(document.getElementById('vinRecommendationModal'));
}

/**
 * Renders the Garage view, displaying a list of the client's cars.
 * Updates the Add Car button state (large dashed if empty, small solid if populated).
 * @param {Array<Object>} cars - Array of car objects belonging to the client.
 */

/* ==========================================
 * 5. GARAGE & CAR MANAGEMENT
 * ========================================== */
/**
    garageCountBadge.textContent = `${cars.length}/10 авто`;
    if (cars.length > 0) {
        requestCarSelect.innerHTML = cars.map(c => `<option value="${c.id}">${escapeHtml(c.brand)} ${escapeHtml(c.model)} (VIN: ${escapeHtml(c.vin)})</option>`).join('');
    } else {
        requestCarSelect.innerHTML = `<option value="">Спочатку додайте авто в гараж</option>`;
    }

    if (cars.length === 0) {
        garageContainer.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 24px;"> Ваш гараж порожній. Додайте перше авто нижче (до 10 машин).</div>`;
        return;
    }

    const addCarBtn = document.querySelector('button[onclick="openAddNewCarModal()"]');
    if (addCarBtn) {
        if (cars.length > 0) {
            addCarBtn.style.border = 'none';
            addCarBtn.style.background = 'var(--primary)';
            addCarBtn.style.color = '#fff';
            addCarBtn.style.padding = '10px';
            addCarBtn.style.width = '100%';
            addCarBtn.style.marginTop = '24px';
            addCarBtn.innerHTML = '<span>+ Додати ще авто</span>';
        } else {
            addCarBtn.style.border = '2px dashed var(--primary)';
            addCarBtn.style.background = 'transparent';
            addCarBtn.style.color = 'var(--primary)';
            addCarBtn.style.padding = '14px';
            addCarBtn.style.width = '100%';
            addCarBtn.innerHTML = '<span>+ Додати авто в гараж</span>';
        }
    }

    garageContainer.innerHTML = cars.map(car => {
        const isNoVin = !car.vin || car.vin.startsWith('NOVIN-');
        const vinDisplay = isNoVin ? '<span style="color:#d97706; font-weight:600;">Не вказано (Рекомендовано додати)</span>' : escapeHtml(car.vin);

        const genDisplay = car.generation ? car.generation : (car.body_type ? car.body_type : '-');
        const engineStr = car.engine_code ? car.engine_code : '-';
        const hpStr = car.horse_power ? car.horse_power : '-';
        const engineDisplay = `${engineStr} | ${hpStr}`;
        const transmissionDisplay = `${car.transmission_type || '-'} ${car.transmission_code ? '('+car.transmission_code+')' : ''}`;

        return `
        <div class="garage-card" style="cursor:pointer; transition:transform 0.2s;" onclick="openCarDetailModal(${car.id})">
            <div class="garage-header-flex">
                <div>
                    <div class="garage-card-title">${escapeHtml(car.brand)} ${escapeHtml(car.model)} ${car.release_date ? `<span style="font-size:13px; color:var(--primary); font-weight:600;">(${escapeHtml(car.release_date)} р.в.)</span>` : ''}</div>
                    <div class="garage-card-vin">VIN: ${vinDisplay}</div>
                </div>
                <div class="brand-emblem-badge">
                    ${getBrandEmblem(car.brand)}
                </div>
            </div>
            
            ${car.custom_photo_url ? `
                <div style="margin-top:10px; width:100%; height:130px; border-radius:10px; overflow:hidden;">
                    <img src="${escapeHtml(car.custom_photo_url)}" alt="${escapeHtml(car.brand)}" style="width:100%; height:100%; object-fit:cover;">
                </div>
            ` : ''}

            <div class="garage-details" style="margin-top:10px;">
                <div><span class="g-label">Кузов / Покоління</span><div class="g-value">${escapeHtml(genDisplay)}</div></div>
                <div><span class="g-label">Рік випуску</span><div class="g-value">${escapeHtml(car.release_date || '-')}</div></div>
                <div><span class="g-label">Двигун & Потужність</span><div class="g-value">${escapeHtml(engineDisplay)}</div></div>
                <div><span class="g-label">Трансмісія</span><div class="g-value">${escapeHtml(transmissionDisplay)}</div></div>
            </div>

            ${isNoVin ? `
                <div style="margin-top:10px; background:#fffbe6; border:1px solid #ffe58f; padding:8px 12px; border-radius:10px; font-size:12px; display:flex; justify-content:space-between; align-items:center; gap:6px;">
                    <span style="color:#d48806; font-weight:600;"> Вкажіть VIN для Бортжурналу та ТО</span>
                    <button class="btn btn-primary" style="width:auto; padding:4px 10px; font-size:11px; white-space:nowrap;" onclick="event.stopPropagation(); openVinRecommendationModal(${car.id}, '${escapeHtml(car.brand)} ${escapeHtml(car.model)}')"> Вказати VIN</button>
                </div>
            ` : ''}

            <div style="display:flex; gap:6px; margin-top:10px;" onclick="event.stopPropagation();">
                <button class="btn btn-secondary" style="font-size:11px; padding:8px; flex:1;" onclick="openCarDetailModal(${car.id})">
                    🏎️ Огляд & Паспорт
                </button>
                <button class="btn btn-secondary" style="font-size:11px; padding:8px; flex:1;" onclick="generateTransferCode(${car.id}, '${escapeHtml(car.brand)} ${escapeHtml(car.model)}')">
                    🔑 PIN для продажу
                </button>
                <button class="btn btn-delete" style="font-size:11px; padding:8px; width:auto;" title="Видалити з гаража" onclick="deleteCarFromGarage(${car.id}, '${escapeHtml(car.brand)}', '${escapeHtml(car.model)}', '${escapeHtml(car.vin)}')">
                    🗑️
                </button>
            </div>
        </div>
    `}).join('');
}


async function generateTransferCode(carId, carName) {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    try {
        const res = await fetch(`${API_BASE_URL}/transfers/generate-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
            body: JSON.stringify({ car_id: carId })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Помилка');

        alert(` ОДНОРАЗОВИЙ SMS PIN-КОД ПЕРЕДАЧІ АВТО:\n\nPIN-КОД: ${data.pin_code}\n\n Код дійсний 15 ХВИЛИН!\n\nПередайте цей 6-значний код покупцю. При введенні у його застосунку авто "${carName}" та вся його історія перейдуть до нього.`);
    } catch (err) {
        showToast(err.message, 'error');
    }
}







/**
 * Renders the active Requests list for the client.
 * Groups items and displays statuses using badges.
 * @param {Array<Object>} requests - Array of request objects.
 */

/* ==========================================
 * 6. REQUESTS & ORDERS HISTORY
 * ========================================== */
function renderRequests(requests) {
    if (requests.length === 0) {
        requestsHistoryContainer.innerHTML = `<div style="color:var(--text-muted); text-align:center; padding:16px;">У вас поки немає надісланих запитів.</div>`;
        return;
    }

    requestsHistoryContainer.innerHTML = requests.map(req => `
        <div class="card" style="margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; font-size:12px; color:var(--text-muted); margin-bottom:6px;">
                <span>Запит #${req.id} від ${formatDate(req.created_at)}</span>
                <span class="badge ${req.status === 'completed' ? 'badge-engine' : 'badge-trans'}">${req.status === 'completed' ? ' Відповідь отримано' : ' В обробці'}</span>
            </div>
            <div style="font-size:14px; font-weight:600; margin-bottom:8px;">"${escapeHtml(req.client_message)}"</div>

            <button class="btn btn-secondary" style="font-size:11px; padding:4px 8px; margin-bottom:8px;" onclick="openChatModal(${req.id})">
                 Чат з експертом по цьому запиту
            </button>

            ${req.proposal ? `
                <div style="background:rgba(15,23,42,0.6); padding:12px; border-radius:10px; border:1px solid rgba(59,130,246,0.3); margin-top:8px;">
                    <div style="color:#60a5fa; font-weight:700; font-size:13px; margin-bottom:6px;"> Кошторис від Експерта:</div>
                    ${req.proposal.manager_comment ? `<div style="font-size:12px; color:var(--text-muted); margin-bottom:8px;"> ${escapeHtml(req.proposal.manager_comment)}</div>` : ''}
                    
                    <form onsubmit="submitOrderFromProposal(event, ${req.proposal.id}, ${req.car_id})">
                        ${req.proposal.items.map((item, idx) => `
                            <div style="margin-bottom:10px; padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.05);">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <div style="font-size:13px; font-weight:600;"> ${idx+1}. ${escapeHtml(item.category_name)}</div>
                                    ${item.oem_number ? `
                                        <span style="background:rgba(16,185,129,0.2); color:#34d399; border:1px solid rgba(16,185,129,0.4); padding:2px 8px; border-radius:12px; font-size:10px; font-weight:700;">
                                             100% Перевірено за OE #${escapeHtml(item.oem_number)}
                                        </span>
                                    ` : `
                                        <span style="background:rgba(245,158,11,0.2); color:#fbbf24; border:1px solid rgba(245,158,11,0.4); padding:2px 8px; border-radius:12px; font-size:10px; font-weight:700;">
                                             Підбір за специфікацією моделі
                                        </span>
                                    `}
                                </div>
                                <div style="margin-top:6px; display:flex; flex-direction:column; gap:4px;">

                                    ${item.alternatives.map((alt, aIdx) => `
                                        <label style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.05); padding:8px 10px; border-radius:6px; font-size:12px; cursor:pointer;">
                                            <div style="display:flex; align-items:center; gap:8px;">
                                                <input type="radio" name="item_${item.id}" value="${alt.brand}|${alt.part_number}|${alt.price}|${item.category_name}|${item.oem_number || ''}" ${aIdx === 0 ? 'checked' : ''}>
                                                <span> <strong>${escapeHtml(alt.brand)}</strong> (${escapeHtml(alt.part_number)})</span>
                                            </div>
                                            <span style="color:#34d399; font-weight:700;">${alt.price} грн</span>
                                        </label>
                                    `).join('')}
                                </div>
                            </div>
                        `).join('')}

                        <div style="margin: 10px 0; font-size: 12px;">
                            <label style="font-weight:600; display:block; margin-bottom:4px;">Адреса доставки Нової Пошти (місто, відділення/поштомат):</label>
                            <input type="text" name="shipping_address" placeholder="наприклад: м. Дніпро, Відділення №12" style="width:100%; padding:8px; border-radius:6px; background:var(--bg-card); color:var(--text-main); border:1px solid var(--border-color); font-size:12px; margin-bottom:8px;" value="${escapeHtml(currentClient?.shipping_address || '')}" required>
                        </div>

                        <div style="margin: 10px 0; font-size: 12px;">
                            <label style="font-weight:600; display:block; margin-bottom:4px;">Оберіть спосіб оплати:</label>
                            <select name="payment_method" style="width:100%; padding:8px; border-radius:6px; background:var(--bg-card); color:var(--text-main); border:1px solid var(--border-color); font-size:12px;">
                                <option value="cash_on_delivery">Накладений платіж Нової Пошти (при отриманні)</option>
                                <option value="fop_prepayment">Передплата на рахунок ФОП (IBAN)</option>
                                <option value="partial_prepayment">Часткова передплата (аванс)</option>
                            </select>
                        </div>

                        <button type="submit" class="btn btn-primary">
                            Оформити замовлення обраних деталей
                        </button>
                    </form>
                </div>
            ` : ''}
        </div>
    `).join('');
}

async function submitOrderFromProposal(e, proposalId, carId) {
    e.preventDefault();
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    const form = e.target;

    const items = [];
    const radios = form.querySelectorAll('input[type="radio"]:checked');
    const paymentMethod = form.querySelector('select[name="payment_method"]').value;
    const shippingAddress = form.querySelector('input[name="shipping_address"]')?.value.trim();

    radios.forEach(radio => {
        const parts = radio.value.split('|');
        if (parts.length >= 4) {
            items.push({
                brand: parts[0],
                part_number: parts[1],
                price: parseFloat(parts[2]),
                category_name: parts[3],
                oem_number: parts[4] || null,
                delivery_term: "1-2 дні"
            });
        }
    });

    if (items.length === 0) {
        showToast('Оберіть хоча б одну деталь для замовлення!', 'error');
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/orders/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
            body: JSON.stringify({
                car_id: carId,
                proposal_id: proposalId,
                payment_method: paymentMethod,
                shipping_address: shippingAddress,
                items
            })
        });

        const order = await res.json();
        if (!res.ok) throw new Error(order.detail || 'Помилка замовлення');

        if (shippingAddress) {
            currentClient.shipping_address = shippingAddress;
            userShippingDisplay.textContent = shippingAddress;
            document.getElementById('profileShipping').textContent = shippingAddress;
        }

        showToast(`Замовлення #${order.id} на суму ${order.total_price} грн оформлено!`);
        await loadMyOrders(token);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

/**
 * Renders the Order History view (completed or processing orders).
 * Allows the user to initiate returns for eligible orders.
 * @param {Array<Object>} orders - Array of order objects.
 */
function renderMyOrders(orders) {
    if (orders.length === 0) {
        myOrdersContainer.innerHTML = `<div style="color:var(--text-muted); text-align:center; padding:16px;">У вас поки немає оформлених замовлень.</div>`;
        return;
    }

    myOrdersContainer.innerHTML = orders.map(order => `
        <div class="card" style="margin-bottom:12px; border-left: 4px solid var(--primary);">
            <div style="display:flex; justify-content:space-between; font-size:12px; color:var(--text-muted); margin-bottom:6px;">
                <span>Замовлення #${order.id} від ${formatDate(order.created_at)}</span>
                <span class="badge ${order.status === 'shipped' ? 'badge-engine' : 'badge-trans'}">
                    ${getStatusTitle(order.status)}
                </span>
            </div>

            <div style="font-size:15px; font-weight:700; color:#34d399; margin-bottom:4px;">
                Сума: ${order.total_price} грн
            </div>

            <div style="font-size:12px; color:#60a5fa; margin-bottom:8px;">
                Оплата: ${getPaymentTitle(order.payment_method)}
            </div>

            ${order.assembly_photo_url ? `
                <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); padding:10px; border-radius:8px; margin:8px 0; font-size:12px;">
                    <div style="color:#34d399; font-weight:700; margin-bottom:4px;">Фотофіксація зібраного товару:</div>
                    <a href="${escapeHtml(order.assembly_photo_url)}" target="_blank" style="color:#60a5fa; word-break:break-all;">${escapeHtml(order.assembly_photo_url)}</a>
                </div>
            ` : ''}

            ${order.ttn_number ? `
                <div style="background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.4); padding:10px; border-radius:8px; margin:8px 0; font-size:12px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="color:#60a5fa; font-weight:700;">ТТН Нової Пошти: ${escapeHtml(order.ttn_number)}</div>
                        <small style="color:var(--text-muted);">Відправка сформована</small>
                    </div>
                    ${order.ttn_tracking_url ? `<a href="${escapeHtml(order.ttn_tracking_url)}" target="_blank" class="btn btn-primary" style="padding:6px 12px; font-size:11px; width:auto; text-decoration:none;">Відстежити</a>` : ''}
                </div>
            ` : ''}

            <div style="font-size:12px; color:var(--text-muted); margin-top:8px;">
                <strong>Склад замовлення:</strong>
                ${order.items.map(i => `<div style="margin-top:2px; color:#f8fafc;">• ${escapeHtml(i.category_name)}: ${escapeHtml(i.brand)} ${escapeHtml(i.part_number)} (${i.price} грн)</div>`).join('')}
            </div>

            <div style="display:flex; gap:6px; margin-top:10px;">
                <button class="btn btn-secondary" style="font-size:11px; padding:6px; flex:1;" onclick="window.open('${API_BASE_URL}/invoices/order/${order.id}', '_blank')">
                    Товарний Чек
                </button>
                <button class="btn btn-secondary" style="font-size:11px; padding:6px; flex:1;" onclick="repeatOrder(${order.id})">
                    Повторити
                </button>
                <button class="btn btn-secondary" style="font-size:11px; padding:6px; flex:1; background:rgba(239,68,68,0.2); border-color:rgba(239,68,68,0.4);" onclick="openReturnModal(${order.id})">
                    Повернення
                </button>
            </div>
        </div>
    `).join('');

}

/**
 * Рендеринг Хронологічної Сервісної Книжки у Гаражі
 */
function renderServiceTimeline(orders) {
    if (!serviceTimelineContainer) return;
    if (orders.length === 0) {
        serviceTimelineContainer.innerHTML = `
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div style="font-size:12px; color:var(--text-muted);">Сервісна книжка поки порожня. Після замовлення тут з'явиться історія ремонту.</div>
            </div>
        `;
        return;
    }

    serviceTimelineContainer.innerHTML = orders.map(o => `
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div style="display:flex; justify-content:space-between; font-size:11px; color:#60a5fa; margin-bottom:4px;">
                <span> ${formatDate(o.created_at)}</span>
                <span>Замовлення #${o.id}</span>
            </div>
            <div style="font-size:13px; font-weight:700;"> Замінені запчастини:</div>
            <div style="font-size:12px; margin-top:2px; color:var(--text-main);">
                ${o.items.map(i => `<div>• ${escapeHtml(i.category_name)} (${escapeHtml(i.brand)} ${escapeHtml(i.part_number)})</div>`).join('')}
            </div>
        </div>
    `).join('');
}

function openReturnModal(orderId) {
    activeReturnOrderId = orderId;
    document.getElementById('returnOrderId').textContent = orderId;
    showModal(returnModal);
}

function closeReturnModal() {
    hideModal(returnModal);
}

async function openChatModal(requestId) {
    activeChatRequestId = requestId;
    document.getElementById('chatRequestId').textContent = requestId;
    showModal(chatModal);
    await loadChatMessages(requestId);
}

function closeChatModal() {
    hideModal(chatModal);
}

async function loadChatMessages(requestId) {
    try {
        const res = await fetch(`${API_BASE_URL}/chat/messages/${requestId}`);
        if (!res.ok) return;
        const messages = await res.json();
        chatMessagesContainer.innerHTML = messages.map(m => `
            <div style="align-self: ${m.sender_type === 'client' ? 'flex-end' : 'flex-start'}; background: ${m.sender_type === 'client' ? 'rgba(59,130,246,0.3)' : 'rgba(255,255,255,0.1)'}; padding:8px 12px; border-radius:10px; max-width:80%; font-size:13px;">
                <div style="font-size:10px; color:var(--text-muted);">${m.sender_type === 'client' ? 'Ви' : 'Експерт'} • ${formatDate(m.created_at)}</div>
                <div>${escapeHtml(m.message)}</div>
                  ${m.attachment_url ? `<div style="margin-top:6px;"><a href="${escapeHtml(m.attachment_url)}" target="_blank"><img src="${escapeHtml(m.attachment_url)}" style="max-width:100%; border-radius:8px;"></a></div>` : ''}
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

async function repeatOrder(orderId) {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    try {
        const res = await fetch(`${API_BASE_URL}/orders/${orderId}/repeat`, {
            method: 'POST',
            headers: { 'X-Auth-Token': token }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Помилка');

        showToast(' Запит на повтор замовлення надіслано експерту!');
        await loadMyRequests(token);
    } catch (err) {
        showToast(` ${err.message}`, 'error');
    }
}

function getStatusTitle(st) {
    const map = {
        'sent_to_preparation': ' В підготовці',
        'assembling': ' Збирається у постачальників',
        'ready_for_shipping': ' Зібрано, готується до відправки',
        'shipped': ' Відправлено Новою Поштою',
        'delivered': ' Отримано клієнтом'
    };
    return map[st] || st;
}

function getPaymentTitle(pm) {
    const map = {
        'cash_on_delivery': ' Накладений платіж Нової Пошти',
        'fop_prepayment': ' Передплата на рахунок ФОП',
        'partial_prepayment': '️ Часткова передплата'
    };
    return map[pm] || pm;
}

/**
 * Logs out the current user by removing tokens from localStorage and resetting UI state.
 */
function handleLogout() {
    if (confirm('Вийти з Особистого Кабінету?')) {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        currentClient = null;
        showAuthScreen();
    }
}

function showAuthScreen() {
    mainScreen.classList.remove('active');
    authScreen.classList.add('active');
}

/**
 * Displays a temporary toast notification on the screen.
 * Automatically dismisses after 3.5 seconds.
 * @param {string} msg - The message to display.
 * @param {string} [type='info'] - The type of toast ('info', 'success', 'error').
 */
function showToast(msg, type = 'info') {
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    toastContainer.appendChild(t);
    setTimeout(() => t.remove(), 4000);
}

function formatDate(iso) {
    if (!iso) return '';
    return new Date(iso).toLocaleDateString('uk-UA');
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

let currentDetailCarId = null;
let currentDetailCarObj = null;

window.openCarDetailModal = function(carId) {
    if (!currentClient || !currentClient.cars) return;
    const car = currentClient.cars.find(c => c.id === carId);
    if (!car) return;

    currentDetailCarId = carId;
    currentDetailCarObj = car;

    const displayVin = car.vin || 'Не вказано';

    document.getElementById('detailCarTitle').textContent = `${car.brand} ${car.model}`;
    document.getElementById('detailCarVinBadge').textContent = `VIN: ${displayVin}`;
    document.getElementById('detailCarBrandEmblem').innerHTML = getBrandEmblem(car.brand);

    const genDisplay = car.generation ? car.generation : (car.body_type ? car.body_type : '-');
    document.getElementById('detailCarGeneration').textContent = genDisplay;
    document.getElementById('detailCarYear').textContent = car.release_date ? `${car.release_date} р.в.` : '-';
    
    const engineDisplay = car.engine_code || '-';
    const hpDisplay = car.horse_power || '-';
    document.getElementById('detailCarEngine').textContent = `${engineDisplay} | ${hpDisplay}`;
    
    document.getElementById('detailCarFuel').textContent = `${car.fuel_type || '-'} | ${car.drive_type || '-'}`;
    document.getElementById('detailCarTrans').textContent = `${car.transmission_type || '-'} ${car.transmission_code ? `(${car.transmission_code})` : ''}`;
    document.getElementById('detailCarColor').textContent = car.color_code || '-';
    document.getElementById('detailCarPlant').textContent = car.assembly_plant || '-';
    document.getElementById('detailCarMileage').textContent = `${(car.mileage || 0).toLocaleString('uk-UA')} км`;

    const heroImg = document.getElementById('carHeroPhoto');
    const logoWrapper = document.getElementById('carLogoPlaceholder');

    if (car.custom_photo_url) {
        heroImg.src = car.custom_photo_url;
        heroImg.style.display = 'block';
        if(logoWrapper) logoWrapper.style.display = 'none';
    } else {
        heroImg.style.display = 'none';
        if(logoWrapper) {
            logoWrapper.style.display = 'flex';
            logoWrapper.innerHTML = getBrandEmblem(car.brand);
        }
    }

    document.getElementById('detailPassportBtn').onclick = () => window.open(`${API_BASE_URL}/invoices/car/${car.id}/passport`, '_blank');
    document.getElementById('detailPinBtn').onclick = () => generateTransferCode(car.id, `${car.brand} ${car.model}`);
    document.getElementById('detailDeleteBtn').onclick = () => deleteCarFromGarage(car.id, car.brand, car.model, car.vin);

    showModal(document.getElementById('carDetailModal'));
};

window.closeCarDetailModal = function() {
    hideModal(document.getElementById('carDetailModal'));
};


window.updateCarMileage = async function() {
    if (!currentDetailCarId) return;
    const mileageInput = document.getElementById('editMileageInput');
    const newMileage = parseInt(mileageInput.value);
    if (!newMileage || newMileage <= 0) {
        showToast(' Будь ласка, введіть дійсний пробіг у кілометрах!', 'error');
        return;
    }

    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    try {
        const res = await fetch(`${API_BASE_URL}/cars/${currentDetailCarId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
            body: JSON.stringify({ mileage: newMileage })
        });
        const updatedCar = await res.json();
        if (!res.ok) throw new Error(updatedCar.detail || 'Помилка оновлення пробігу');

        showToast(` Пробіг авто оновлено на ${newMileage.toLocaleString('uk-UA')} км!`);
        await refreshGarage(token);
        openCarDetailModal(currentDetailCarId);
    } catch (err) {
        showToast(err.message, 'error');
    }
};

window.deleteCarFromGarage = async function(carId, brand, model, vin) {
    const confirmMsg = `Видалити авто ${brand} ${model} (VIN: ${vin}) з вашого гаража?`;
    if (!confirm(confirmMsg)) return;

    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    try {
        const res = await fetch(`${API_BASE_URL}/clients/me/cars/${carId}`, {
            method: 'DELETE',
            headers: { 'X-Auth-Token': token }
        });

        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || 'Помилка видалення');
        }

        showToast(` Автомобіль ${brand} ${model} видалено з вашого гаража та бази даних.`);
        closeCarDetailModal();
        await refreshGarage(token);
    } catch (err) {
        showToast(err.message, 'error');
    }
};

async function handleChatImageUpload(file, callback) {
    try {
        showToast('Завантаження фото...', 'info');
        const formData = new FormData();
        formData.append('reqtype', 'fileupload');
        formData.append('fileToUpload', file);
        const res = await fetch('https://catbox.moe/user/api.php', { method: 'POST', body: formData });
        if(!res.ok) throw new Error('Помилка завантаження');
        const url = await res.text();
        showToast('Фото завантажено!', 'success');
        callback(url);
    } catch(err) {
        showToast('Не вдалося завантажити фото: ' + err.message, 'error');
    }
}
window.handleChatImageUpload = handleChatImageUpload;

window.uploadAndSendchatInputFile = async function(file) {
    if(!file || !activeChatRequestId) return;
    const token = localStorage.getItem(TOKEN_STORAGE_KEY) || localStorage.getItem('admin_token');
    handleChatImageUpload(file, async (url) => {
        try {
            const res = await fetch(`${API_BASE_URL}/chat/messages?sender_type=client`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify({ request_id: activeChatRequestId, message: '📷 Фото', attachment_url: url })
            });
            if(!res.ok) throw new Error('Помилка відправки');
            if (typeof loadChatMessages === 'function') await loadChatMessages(activeChatRequestId);
            if (typeof loadAdminChatMessages === 'function') await loadAdminChatMessages(activeChatRequestId);
        } catch(err) {
            showToast(err.message, 'error');
        }
    });
};


window.uploadCustomCarPhoto = async function(file) {
    if(!file || !currentDetailCarId) return;
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (typeof handleChatImageUpload === 'function') {
        handleChatImageUpload(file, async (url) => {
            try {
                const res = await fetch(`${API_BASE_URL}/cars/${currentDetailCarId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                    body: JSON.stringify({ custom_photo_url: url })
                });
                const updatedCar = await res.json();
                if(!res.ok) throw new Error(updatedCar.detail || 'Помилка оновлення фото авто');
                showToast('Фото авто успішно оновлено!', 'success');
                await refreshGarage(token);
                openCarDetailModal(currentDetailCarId);
            } catch(err) {
                showToast(err.message, 'error');
            }
        });
    } else {
        showToast('Система завантаження тимчасово недоступна.', 'error');
    }
};


const catalogStructure = {
    engine: {
        title: "Двигун & Олива",
        items: [
            "Мастило моторне", "Фільтр масляний", "Комплект ГРМ", "Помпа водяна", 
            "Прокладка ГБЦ", "Прокладка клапанної кришки", "Сальники", "Поршневі кільця", 
            "Вкладиші", "Опорні подушки двигуна"
        ]
    },
    brakes: {
        title: "Гальмівна система",
        items: [
            "Гальмівні колодки (передні)", "Гальмівні колодки (задні)", 
            "Гальмівні диски (передні)", "Гальмівні диски (задні)",
            "Гальмівна рідина", "Ремкомплект супорта", "Гальмівні шланги", "Трос ручника"
        ]
    },
    suspension: {
        title: "Ходова & Підвіска",
        items: [
            "Амортизатори (передні)", "Амортизатори (задні)", 
            "Стійки стабілізатора", "Втулки стабілізатора", 
            "Важелі підвіски", "Сайлентблоки", "Кульові опори", 
            "Ступичні підшипники", "Пружини"
        ]
    },
    electrical: {
        title: "Електрика & Свічки",
        items: [
            "Свічки запалювання", "Свічки розжарювання", 
            "Акумулятор (АКБ)", "Котушка запалювання", 
            "Високовольтні дроти", "Генератор", "Стартер", "Лампи"
        ]
    },
    cooling: {
        title: "Охолодження & Клімат",
        items: [
            "Радіатор охолодження", "Антифриз", "Термостат", 
            "Вентилятор радіатора", "Радіатор кондиціонера", 
            "Фреон", "Фільтр салону", "Компресор кондиціонера"
        ]
    },
    transmission: {
        title: "Трансмісія & Зчеплення",
        items: [
            "Мастило КПП", "Мастило АКПП", "Комплект зчеплення", 
            "Маховик", "Вижимний підшипник", "ШРУС (Граната)", 
            "Піввісь", "Підвісний підшипник", "Сальники приводу"
        ]
    }
};

window.openSubCatalog = function(categoryKey) {
    const data = catalogStructure[categoryKey];
    if(!data) return;

    document.getElementById('subCatalogTitle').innerText = data.title;
    
    const listContainer = document.getElementById('subCatalogList');
    listContainer.innerHTML = '';
    
    // Add "All Category" button
    const allBtn = document.createElement('button');
    allBtn.style = 'padding:12px; background:var(--primary); color:white; border:none; border-radius:8px; font-weight:600; cursor:pointer; text-align:left; font-size:14px;';
    allBtn.innerText = '➡️ ' + data.title + ' (Весь вузол)';
    allBtn.onclick = () => {
        applyPreset(data.title);
        hideModal(document.getElementById('subCatalogModal'));
    };
    listContainer.appendChild(allBtn);

    // Add individual items
    data.items.forEach(item => {
        const btn = document.createElement('button');
        btn.style = 'padding:12px; background:#f1f5f9; color:var(--text-main); border:none; border-radius:8px; font-weight:500; cursor:pointer; text-align:left; font-size:14px; transition:background 0.2s;';
        btn.innerText = item;
        btn.onmouseover = () => btn.style.background = '#e2e8f0';
        btn.onmouseout = () => btn.style.background = '#f1f5f9';
        btn.onclick = () => {
            applyPreset(item);
            hideModal(document.getElementById('subCatalogModal'));
        };
        listContainer.appendChild(btn);
    });
    
    showModal(document.getElementById('subCatalogModal'));
};


const SUB_CATALOGS = {
    'engine': {
        title: 'Двигун & Олива',
        items: [
            { id: 'engine_oil', name: 'Олива ДВС' },
            { id: 'timing_belt', name: 'Комплект ГРМ' },
            { id: 'water_pump', name: 'Водяна помпа' },
            { id: 'filters', name: 'Фільтри (масляний, повітряний, паливний)' },
            { id: 'gaskets', name: 'Прокладки та сальники' },
            { id: 'engine_mounts', name: 'Подушки двигуна' }
        ]
    },
    'brakes': {
        title: 'Гальмівна система',
        items: [
            { id: 'brake_pads', name: 'Гальмівні колодки' },
            { id: 'brake_discs', name: 'Гальмівні диски' },
            { id: 'brake_fluid', name: 'Гальмівна рідина' },
            { id: 'calipers', name: 'Супорти та ремкомплекти' },
            { id: 'brake_hoses', name: 'Гальмівні шланги' }
        ]
    },
    'suspension': {
        title: 'Ходова & Підвіска',
        items: [
            { id: 'shock_absorbers', name: 'Амортизатори' },
            { id: 'control_arms', name: 'Важелі підвіски' },
            { id: 'ball_joints', name: 'Кульові опори' },
            { id: 'bushings', name: 'Сайлентблоки' },
            { id: 'tie_rods', name: 'Рульові тяги та наконечники' },
            { id: 'wheel_bearings', name: 'Ступичні підшипники' }
        ]
    },
    'electrical': {
        title: 'Електрика & Свічки',
        items: [
            { id: 'spark_plugs', name: 'Свічки запалювання / розжарювання' },
            { id: 'battery', name: 'Акумулятор (АКБ)' },
            { id: 'ignition_coils', name: 'Котушки запалювання' },
            { id: 'alternator', name: 'Генератор та стартер' },
            { id: 'sensors', name: 'Датчики (лямбда, ДМРВ тощо)' },
            { id: 'bulbs', name: 'Автолампи' }
        ]
    },
    'cooling': {
        title: 'Охолодження & Клімат',
        items: [
            { id: 'antifreeze', name: 'Антифриз' },
            { id: 'radiator', name: 'Радіатор охолодження' },
            { id: 'thermostat', name: 'Термостат' },
            { id: 'ac_compressor', name: 'Компресор кондиціонера' },
            { id: 'cabin_filter', name: 'Фільтр салону' }
        ]
    },
    'transmission': {
        title: 'Трансмісія & Зчеплення',
        items: [
            { id: 'trans_oil', name: 'Олива КПП (ATF / MTF)' },
            { id: 'clutch_kit', name: 'Комплект зчеплення' },
            { id: 'flywheel', name: 'Маховик' },
            { id: 'cv_joints', name: 'Шруси та півосі' },
            { id: 'driveshaft', name: 'Карданний вал та підвісні' }
        ]
    }
};

window.openSubCatalog = function(catKey) {
    if (!currentDetailCarId) return showToast('Спочатку оберіть авто в гаражі!', 'error');
    const cat = SUB_CATALOGS[catKey];
    if (!cat) return;
    
    document.getElementById('subCatalogTitle').textContent = cat.title;
    
    const listHtml = cat.items.map(item => `
        <div class="card parts-cat-card" style="margin-bottom: 8px;" onclick="addPartFromSubCatalog('${item.name}')">
            <div class="cat-info" style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                <div class="cat-text">
                    <span class="cat-title" style="font-size: 14px;">${item.name}</span>
                </div>
                <div class="cat-arrow">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"></path></svg>
                </div>
            </div>
        </div>
    `).join('');
    
    document.getElementById('subCatalogList').innerHTML = listHtml;
    
    const modals = document.querySelectorAll('#subCatalogModal');
    if (modals.length > 0) {
        showModal(modals[0]);
    }
};

window.addPartFromSubCatalog = function(partName) {
    const modals = document.querySelectorAll('#subCatalogModal');
    if (modals.length > 0) {
        hideModal(modals[0]);
    }
    
    const textEl = document.getElementById('requestText');
    if (textEl.value.trim() === '') {
        textEl.value = partName;
    } else {
        textEl.value = textEl.value.trim() + ', ' + partName;
    }
    
    // Automatically set the car select to the currently selected car
    const requestCarSelect = document.getElementById('requestCarSelect');
    if (currentDetailCarId && requestCarSelect) {
        requestCarSelect.value = currentDetailCarId;
    }
    
    showToast('Деталь додано до запиту!', 'success');
    switchNavTab('request');
};

// --- Password visibility toggle ---
function togglePassword(btnOrId, btnEl) {
    var btn = btnEl || btnOrId;
    var wrapper = btn.closest('.password-wrapper');
    if (!wrapper) return;
    var input = wrapper.querySelector('input');
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>';
    } else {
        input.type = 'password';
        btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
    }
}
window.togglePassword = togglePassword;

