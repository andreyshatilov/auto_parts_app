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

const CAR_DATABASE = {
    "Acura": ["MDX", "RDX", "TLX", "ILX", "TSX", "ZDX", "Integra", "RLX"],
    "Alfa Romeo": ["Giulia", "Stelvio", "159", "Giulietta", "Tonale", "Mito", "Brera", "147", "156", "4C"],
    "Audi": ["A1", "A3", "A4", "A5", "A6", "A7", "A8", "Q2", "Q3", "Q4 e-tron", "Q5", "Q7", "Q8", "e-tron", "TT", "R8", "RS3", "RS4", "RS5", "RS6", "RS7", "RS Q8", "80 / 100"],
    "BMW": ["1 Series", "2 Series", "3 Series", "4 Series", "5 Series", "6 Series", "7 Series", "8 Series", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "XM", "Z4", "i3", "i4", "i7", "iX", "M2", "M3", "M4", "M5", "M8"],
    "BYD": ["Song Plus", "Tang", "Han", "Yuan Plus / Atto 3", "Dolphin", "Seal", "Qin Plus"],
    "Cadillac": ["Escalade", "XT5", "XT4", "XT6", "CTS", "ATS", "SRX", "Lyriq"],
    "Changan": ["CS35 Plus", "CS55 Plus", "CS75 Plus", "UNI-K", "UNI-V", "UNI-T"],
    "Chery": ["Tiggo 2", "Tiggo 4", "Tiggo 7 Pro", "Tiggo 8 Pro", "Amulet", "QQ", "Arrizo 6"],
    "Chevrolet": ["Cruze", "Aveo", "Captiva", "Lacetti", "Camaro", "Tahoe", "Suburban", "Corvette", "Bolt EV", "Equinox", "Trax", "Epica", "Orlando", "Spark", "Evanda", "Niva"],
    "Chrysler": ["300C", "Pacificia", "Town & Country", "Voyager", "200", "Sebring", "PT Cruiser"],
    "Citroen": ["C4", "C5", "C3", "C3 Aircross", "C5 Aircross", "Berlingo", "Jumper", "Jumpy", "SpaceTourer", "C-Elysee", "C4 Picasso", "C1", "C2", "Xsara"],
    "Cupra": ["Formentor", "Born", "Ateca", "Leon"],
    "Dacia": ["Duster", "Logan", "Sandero", "Jogger", "Spring", "Dokker", "Lodgy"],
    "Daewoo": ["Lanos", "Sens", "Matiz", "NEXIA", "Nubira", "Gentra", "Tacuma", "Esperanto"],
    "Dodge": ["Challenger", "Charger", "Durango", "Journey", "Ram 1500", "Caliber", "Dart", "Avenger", "Grand Caravan", "Nitro"],
    "Fiat": ["500", "500X", "Doblo", "Ducato", "Punto", "Tipo", "Panda", "Fiorino", "Freemont", "Bravo", "Scudo"],
    "Ford": ["Focus", "Fusion (US)", "Fusion (EU)", "Mondeo", "Fiesta", "Kuga", "Escape", "Explorer", "Edge", "EcoSport", "Mustang", "Mustang Mach-E", "Transit", "Custom", "C-Max", "S-Max", "Galaxy", "Ranger", "F-150", "Scorpio", "Sierra"],
    "GAZ / ГАЗ": ["24 Волга", "3110 Волга", "Газель", "Газель Next", "Соболь"],
    "Geely": ["Coolray", "Atlas Pro", "Monjaro", "Tugella", "Emgrand", "Geometry C", "CK", "MK"],
    "Genesis": ["G70", "G80", "G90", "GV70", "GV80"],
    "Great Wall / Haval": ["H6", "Jolion", "F7", "H9", "Dargo", "Hover H3/H5", "Wingle"],
    "Honda": ["Civic", "CR-V", "Accord", "HR-V", "Pilot", "Fit / Jazz", "Insight", "Odyssey", "Element", "Ridgeline", "e:NS1"],
    "Hyundai": ["Tucson", "Santa Fe", "Elantra", "Sonata", "Accent", "i10", "i20", "i30", "i40", "Kona", "Palisade", "Getz", "IX35", "Ioniq 5", "Ioniq 6", "Staria", "H-1 / Starex", "Matrix", "Coupe"],
    "Infiniti": ["FX35 / QX70", "FX37", "Q50", "Q60", "QX60", "QX80", "EX35 / QX50", "G35 / G37", "M37 / Q70"],
    "Jaguar": ["F-Pace", "E-Pace", "I-Pace", "XF", "XJ", "XE", "F-Type"],
    "Jeep": ["Grand Cherokee", "Cherokee", "Compass", "Renegade", "Wrangler", "Patriot", "Commander", "Gladiator"],
    "Kia": ["Sportage", "Ceed", "Optima", "Sorento", "Rio", "K5", "Stinger", "Telluride", "Soul", "Cerato", "Niro", "EV6", "Carnival", "Mohave", "Picanto", "Magentis"],
    "Lada / ВАЗ": ["2101-2107", "2108 / 2109 / 21099", "2110 / 2111 / 2112", "Samara", "Kalina", "Priora", "Granta", "Vesta", "Niva / 4x4", "XRAY"],
    "Land Rover": ["Range Rover", "Range Rover Sport", "Range Rover Evoque", "Discovery", "Discovery Sport", "Defender", "Velar", "Freelander"],
    "Lexus": ["RX 300/350/450h", "NX 200/300/350h", "GX 460/550", "LX 470/570/600", "ES 250/300h/350", "IS 250/300/350", "GS 300/350", "UX 200/250h", "LS 460/500", "CT 200h"],
    "Lincoln": ["MKZ", "MKX", "Nautilus", "Aviator", "Navigator", "Corsair", "Town Car"],
    "Maserati": ["Ghibli", "Levante", "Quattroporte", "Grecale"],
    "Mazda": ["3", "6", "CX-3", "CX-5", "CX-7", "CX-9", "CX-30", "CX-50", "CX-60", "MX-5", "2", "323 / 626", "RX-8"],
    "Mercedes-Benz": ["A-Class", "B-Class", "C-Class", "E-Class", "S-Class", "CLA", "CLS", "GLA", "GLB", "GLC", "GLE", "GLS", "G-Class (Geländewagen)", "Vito", "V-Class", "Sprinter", "ML-Class", "GL-Class", "W124 / W210 / W211", "CLK"],
    "MG": ["ZS", "HS", "MG 4", "MG 5", "MG 350"],
    "Mini": ["Cooper", "Countryman", "Clubman", "Paceman"],
    "Mitsubishi": ["Outlander", "Lancer", "Pajero", "Pajero Sport", "ASX", "L200", "Eclipse Cross", "Galant", "Colt", "Grandis"],
    "Nissan": ["Qashqai", "X-Trail", "Rogue", "Juke", "Leaf", "Almera", "Teana", "Patrol", "Navara", "Murano", "Micra", "Note", "Pathfinder", "Tiida", "Sentra", "Maxima", "350Z / 370Z", "Ariya"],
    "Opel": ["Astra F/G/H/J/K", "Insignia", "Vectra A/B/C", "Zafira", "Mokka", "Vivaro", "Corsa", "Omega", "Meriva", "Combo", "Crossland", "Grandland"],
    "Peugeot": ["208", "308", "407", "508", "2008", "3008", "5008", "Partner", "Rifter", "Boxer", "Expert", "206", "207", "307", "406"],
    "Porsche": ["Cayenne", "Macan", "Panamera", "911 Carrera", "Taycan", "Boxster", "Cayman"],
    "Renault": ["Megane", "Duster", "Logan", "Sandero", "Kadjar", "Koleos", "Scenic", "Fluence", "Trafic", "Master", "Clio", "Kangoo", "Symbol", "Arkana", "Zoe"],
    "SAAB": ["9-3", "9-5", "900"],
    "SEAT": ["Leon", "Ibiza", "Ateca", "Tarraco", "Alhambra", "Altea", "Toledo", "Arona"],
    "Skoda": ["Octavia Tour/A5/A7/A8", "Superb", "Kodiaq", "Karoq", "Fabia", "Rapid", "Scala", "Kamiq", "Yeti", "Felicia", "Enyaq"],
    "Smart": ["Fortwo", "Forfour"],
    "SsangYong / KGM": ["Korando", "Rexton", "Kyron", "Actyon", "Tivoli", "Rodius"],
    "Subaru": ["Forester", "Outback", "Legacy", "Impreza", "XV / Crosstrek", "Tribeca", "BRZ", "Solterra"],
    "Suzuki": ["Grand Vitara", "Vitara", "SX4", "Jimny", "Swift", "Liana", "Splash"],
    "Tesla": ["Model 3", "Model Y", "Model S", "Model X", "Cybertruck"],
    "Toyota": ["Camry", "Corolla", "RAV4", "Land Cruiser 200/300", "Land Cruiser Prado 120/150/250", "Highlander", "C-HR", "Yaris", "Avensis", "Hilux", "Prius", "Venza", "Sequoia", "Tundra", "Tacoma", "Sienna", "Auris", "Matrix", "Solara"],
    "Volkswagen": ["Golf III/IV/V/VI/VII/VIII", "Passat B5/B6/B7/B8/NMS", "Tiguan", "Touareg", "Jetta", "Polo", "Arteon", "Transporter T4/T5/T6", "Multivan", "Caddy", "ID.4", "CC", "Amarok", "Bora", "Touran", "Sharan", "Taos"],
    "Volvo": ["XC60", "XC90", "XC40", "S60", "S90", "V60", "V90", "V40", "S80", "V50", "C30", "XC70"],
    "ZAZ / ЗАЗ": ["Lanos / Chance", "Sens", "Forza", "Vida", "Tavria", "Slavuta"]
};

document.addEventListener('DOMContentLoaded', () => {
    initBrandAndModelSelects();
    initApp();
    setupEventListeners();
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

                        let brandFound = Array.from(brandSelect.options).find(opt => opt.value.toUpperCase() === data.brand.toUpperCase());
                        if (brandFound) {
                            brandSelect.value = brandFound.value;
                        } else {
                            brandSelect.value = '__custom__';
                            document.getElementById('clientCustomBrandInput').value = data.brand;
                        }
                        brandSelect.onchange();

                        if (data.model) {
                            let modelFound = Array.from(modelSelect.options).find(opt => opt.value.toUpperCase() === data.model.toUpperCase());
                            if (modelFound) {
                                modelSelect.value = modelFound.value;
                            } else {
                                modelSelect.value = '__custom__';
                                document.getElementById('clientCustomModelInput').value = data.model;
                            }
                            modelSelect.onchange();
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

                        showToast(`⚡ ${data.brand} ${data.model || ''} ${data.release_year ? '(' + data.release_year + ')' : ''} розпізнано за VIN!`);
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
                            showToast(`⚡ ${data.brand} ${data.model || ''} (${data.release_year || ''}) розпізнано за VIN!`);
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
                showToast('⚠️ VIN-код повинен містити ровно 17 символів!', 'error');
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
                }

                const res = await fetch(`${API_BASE_URL}/cars/${carId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                    body: JSON.stringify(updatePayload)
                });
                const car = await res.json();
                if (!res.ok) throw new Error(car.detail || 'Помилка оновлення VIN');

                showToast(`🎉 VIN-код збережено! Відкрито доступ до Сервісного Бортжурналу та ТО для ${car.brand} ${car.model}!`);
                closeVinRecommendationModal();
                await refreshGarage(token);
            } catch (err) {
                showToast(`❌ ${err.message}`, 'error');
            }
        });
    }

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            first_name: document.getElementById('regFirstName').value.trim(),
            last_name: document.getElementById('regLastName').value.trim(),
            phone: document.getElementById('regPhone').value.trim(),
            has_messenger: document.getElementById('regHasMessenger').checked
        };
        try {
            const res = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка');

            localStorage.setItem(TOKEN_STORAGE_KEY, data.auth_token);
            currentClient = data.client;
            showToast(`✅ Ласкаво просимо, ${currentClient.first_name}!`);
            showMainScreen(currentClient);
        } catch (err) {
            showToast(`❌ ${err.message}`, 'error');
        }
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const phone = document.getElementById('loginPhone').value.trim();
        try {
            const res = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка');

            localStorage.setItem(TOKEN_STORAGE_KEY, data.auth_token);
            currentClient = data.client;
            showToast(`👋 З поверненням, ${currentClient.first_name}!`);
            showMainScreen(currentClient);
        } catch (err) {
            showToast(`❌ ${err.message}`, 'error');
        }
    });

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
            if (!res.ok) throw new Error(car.detail || 'Помилка прийому авто');

            showToast(`🎉 Вітаємо! Автомобіль ${car.brand} ${car.model} та вся його історія прийняті у ваш гараж!`);
            document.getElementById('pinInput').value = '';
            await refreshGarage(token);
        } catch (err) {
            showToast(`❌ ${err.message}`, 'error');
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
            showToast('⚠️ Будь ласка, оберіть або вкажіть марку та модель авто!', 'error');
            return;
        }

        let vinValue = clientVinInput.value.trim();
        if (!vinValue) {
            vinValue = 'NOVIN-' + Math.random().toString(36).substring(2, 11).toUpperCase();
        } else if (vinValue.length !== 17) {
            showToast('⚠️ VIN-код повинен містити ровно 17 символів (або залиште порожнім)!', 'error');
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
        if (genVal) modParts.push(`Покоління: ${genVal}`);
        if (restyleVal) modParts.push(restyleVal);
        const modificationStr = modParts.length > 0 ? modParts.join(' | ') : null;

        const carData = {
            vin: vinValue,
            brand: finalBrand,
            model: finalModel,
            modification: modificationStr,
            release_date: document.getElementById('clientYearSelect')?.value || null,
            engine_code: engineVal || null,
            transmission_type: document.getElementById('clientTransInput').value || null
        };
        try {
            const res = await fetch(`${API_BASE_URL}/clients/me/cars`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify(carData)
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка');

            showToast(`🚘 ${data.brand} ${data.model} додано у ваш Гараж!`);
            addGarageCarForm.reset();
            initBrandAndModelSelects();
            clientVinCounter.textContent = '0/17';
            await refreshGarage(token);

            if (vinValue.startsWith('NOVIN-')) {
                openVinRecommendationModal(data.id, `${data.brand} ${data.model}`);
            }
        } catch (err) {
            showToast(`❌ ${err.message}`, 'error');
        }
    });

    requestForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);
        const carId = parseInt(requestCarSelect.value);
        const text = document.getElementById('requestText').value.trim();

        if (!carId) {
            showToast('⚠️ Оберіть авто з гаража!', 'error');
            return;
        }

        try {
            const res = await fetch(`${API_BASE_URL}/requests/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify({ car_id: carId, client_message: text })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка надсилання');

            showToast('📨 Запит на підбір надіслано експерту!');
            document.getElementById('requestText').value = '';
            await loadMyRequests(token);
        } catch (err) {
            showToast(`❌ ${err.message}`, 'error');
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
            if (!res.ok) throw new Error(data.detail || 'Помилка');

            showToast('🔄 Заявка на повернення товару надіслана!');
            closeReturnModal();
            await loadMyOrders(token);
        } catch (err) {
            showToast(`❌ ${err.message}`, 'error');
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
            if (!res.ok) throw new Error(data.detail || 'Помилка');

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
                if (!res.ok) throw new Error(updatedClient.detail || 'Помилка оновлення профілю');

                currentClient = updatedClient;
                showMainScreen(currentClient);
                showToast('Профіль успішно оновлено!');
                closeEditProfileModal();
            } catch (err) {
                showToast(err.message, 'error');
            }
        });
    }
}

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

function openEditProfileModal() {
    if (!currentClient) return;
    document.getElementById('editFirstName').value = currentClient.first_name || '';
    document.getElementById('editLastName').value = currentClient.last_name || '';
    document.getElementById('editEmail').value = currentClient.email || '';
    document.getElementById('editShipping').value = currentClient.shipping_address || '';
    document.getElementById('editProfileModal').style.display = 'flex';
}

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
    otherBrandOpt.textContent = '➕ Інша марка (вказати вручну)';
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
            customBrandInput.value = '';
        }

        if (isCustomModel || isCustomBrand) {
            customRow.style.display = 'flex';
            customModelGroup.style.display = 'block';
            customModelInput.required = true;
        } else {
            customModelGroup.style.display = 'none';
            customModelInput.required = false;
            customModelInput.value = '';
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
            optCustom.textContent = '➕ Інша модель (вказати вручну)';
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
            optCustom.textContent = '➕ Інша модель (вказати вручну)';
            modelSelect.appendChild(optCustom);
        }

        updateCustomFieldsVisibility();
    };

    modelSelect.onchange = () => {
        updateCustomFieldsVisibility();
    };
}

function getBrandEmblem(brandName) {
    if (!brandName) return 'CAR';
    const b = brandName.trim().toUpperCase();
    if (b.includes('BMW')) return 'BMW';
    if (b.includes('AUDI')) return 'AUDI';
    if (b.includes('MERCEDES') || b.includes('BENZ')) return 'BENZ';
    if (b.includes('CHEVROLET') || b.includes('CHEVY')) return 'CHEVY';
    if (b.includes('VOLKSWAGEN') || b.includes('VW')) return 'VW';
    if (b.includes('TOYOTA')) return 'TOYOTA';
    if (b.includes('HONDA')) return 'HONDA';
    if (b.includes('FORD')) return 'FORD';
    if (b.includes('LEXUS')) return 'LEXUS';
    if (b.includes('PORSCHE')) return 'PORSCHE';
    if (b.includes('HYUNDAI')) return 'HYUNDAI';
    if (b.includes('KIA')) return 'KIA';
    if (b.includes('NISSAN')) return 'NISSAN';
    if (b.includes('MAZDA')) return 'MAZDA';
    if (b.includes('VOLVO')) return 'VOLVO';
    return brandName.substring(0, 4).toUpperCase();
}

function openVinRecommendationModal(carId, carName) {
    document.getElementById('addVinCarId').value = carId;
    document.getElementById('vinModalCarName').textContent = `Для автомобіля: ${carName}`;
    document.getElementById('addVinInput').value = '';
    document.getElementById('addVinCounter').textContent = '0/17';
    document.getElementById('vinRecommendationModal').style.display = 'flex';
}

function closeVinRecommendationModal() {
    document.getElementById('vinRecommendationModal').style.display = 'none';
}

function renderGarage(cars) {
    garageCountBadge.textContent = `${cars.length}/10 авто`;
    if (cars.length > 0) {
        requestCarSelect.innerHTML = cars.map(c => `<option value="${c.id}">${escapeHtml(c.brand)} ${escapeHtml(c.model)} (VIN: ${escapeHtml(c.vin)})</option>`).join('');
    } else {
        requestCarSelect.innerHTML = `<option value="">Спочатку додайте авто в гараж</option>`;
    }

    if (cars.length === 0) {
        garageContainer.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 24px;">🚗 Ваш гараж порожній. Додайте перше авто нижче (до 10 машин).</div>`;
        return;
    }

    garageContainer.innerHTML = cars.map(car => {
        const isNoVin = !car.vin || car.vin.startsWith('NOVIN-');
        const vinDisplay = isNoVin ? '<span style="color:#d97706; font-weight:600;">Не вказано (Рекомендовано додати)</span>' : escapeHtml(car.vin);

        return `
        <div class="garage-card">
            <div class="garage-header-flex">
                <div>
                    <div class="garage-card-title">${escapeHtml(car.brand)} ${escapeHtml(car.model)} ${car.release_date ? `<span style="font-size:13px; color:var(--primary); font-weight:600;">(${escapeHtml(car.release_date)} р.в.)</span>` : ''}</div>
                    <div class="garage-card-vin">VIN: ${vinDisplay}</div>
                </div>
                <div class="brand-emblem-badge">
                    ${getBrandEmblem(car.brand)}
                </div>
            </div>
            
            <div class="garage-details">
                <div><span class="g-label">КУЗОВ / ПОКОЛІННЯ</span><div class="g-value">${escapeHtml(car.modification || '—')}</div></div>
                <div><span class="g-label">РІК ВИПУСКУ</span><div class="g-value">${escapeHtml(car.release_date || '—')}</div></div>
                <div><span class="g-label">ДВИГУН</span><div class="g-value">${escapeHtml(car.engine_code || '—')}</div></div>
                <div><span class="g-label">ТРАНСМІСІЯ</span><div class="g-value">${escapeHtml(car.transmission_type || '—')} ${escapeHtml(car.transmission_code || '')}</div></div>
            </div>

            ${isNoVin ? `
                <div style="margin-top:10px; background:#fffbe6; border:1px solid #ffe58f; padding:8px 12px; border-radius:10px; font-size:12px; display:flex; justify-content:space-between; align-items:center; gap:6px;">
                    <span style="color:#d48806; font-weight:600;">💡 Вкажіть VIN для Бортжурналу та ТО</span>
                    <button class="btn btn-primary" style="width:auto; padding:4px 10px; font-size:11px; white-space:nowrap;" onclick="openVinRecommendationModal(${car.id}, '${escapeHtml(car.brand)} ${escapeHtml(car.model)}')">✏️ Вказати VIN</button>
                </div>
            ` : ''}

            <div style="display:flex; gap:6px; margin-top:8px;">
                <button class="btn btn-secondary" style="font-size:11px; padding:8px; flex:1;" onclick="window.open('${API_BASE_URL}/invoices/car/${car.id}/passport', '_blank')">
                    Сервісний Паспорт
                </button>
                <button class="btn btn-secondary" style="font-size:11px; padding:8px; flex:1;" onclick="generateTransferCode(${car.id}, '${escapeHtml(car.brand)} ${escapeHtml(car.model)}')">
                    PIN для продажу
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

        alert(`📲 ОДНОРАЗОВИЙ SMS PIN-КОД ПЕРЕДАЧІ АВТО:\n\nPIN-КОД: ${data.pin_code}\n\n⏱️ Код дійсний 15 ХВИЛИН!\n\nПередайте цей 6-значний код покупцю. При введенні у його застосунку авто "${carName}" та вся його історія перейдуть до нього.`);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function applyPreset(text) {
    document.getElementById('requestText').value = text;
    showToast('Комплект додано в форму запиту!');
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

function renderRequests(requests) {
    if (requests.length === 0) {
        requestsHistoryContainer.innerHTML = `<div style="color:var(--text-muted); text-align:center; padding:16px;">У вас поки немає надісланих запитів.</div>`;
        return;
    }

    requestsHistoryContainer.innerHTML = requests.map(req => `
        <div class="card" style="margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; font-size:12px; color:var(--text-muted); margin-bottom:6px;">
                <span>Запит #${req.id} від ${formatDate(req.created_at)}</span>
                <span class="badge ${req.status === 'completed' ? 'badge-engine' : 'badge-trans'}">${req.status === 'completed' ? '✓ Відповідь отримано' : '⏳ В обробці'}</span>
            </div>
            <div style="font-size:14px; font-weight:600; margin-bottom:8px;">"${escapeHtml(req.client_message)}"</div>

            <button class="btn btn-secondary" style="font-size:11px; padding:4px 8px; margin-bottom:8px;" onclick="openChatModal(${req.id})">
                💬 Чат з експертом по цьому запиту
            </button>

            ${req.proposal ? `
                <div style="background:rgba(15,23,42,0.6); padding:12px; border-radius:10px; border:1px solid rgba(59,130,246,0.3); margin-top:8px;">
                    <div style="color:#60a5fa; font-weight:700; font-size:13px; margin-bottom:6px;">📋 Кошторис від Експерта:</div>
                    ${req.proposal.manager_comment ? `<div style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">💬 ${escapeHtml(req.proposal.manager_comment)}</div>` : ''}
                    
                    <form onsubmit="submitOrderFromProposal(event, ${req.proposal.id}, ${req.car_id})">
                        ${req.proposal.items.map((item, idx) => `
                            <div style="margin-bottom:10px; padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.05);">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <div style="font-size:13px; font-weight:600;">📦 ${idx+1}. ${escapeHtml(item.category_name)}</div>
                                    ${item.oem_number ? `
                                        <span style="background:rgba(16,185,129,0.2); color:#34d399; border:1px solid rgba(16,185,129,0.4); padding:2px 8px; border-radius:12px; font-size:10px; font-weight:700;">
                                            ✅ 100% Перевірено за OE #${escapeHtml(item.oem_number)}
                                        </span>
                                    ` : `
                                        <span style="background:rgba(245,158,11,0.2); color:#fbbf24; border:1px solid rgba(245,158,11,0.4); padding:2px 8px; border-radius:12px; font-size:10px; font-weight:700;">
                                            ℹ️ Підбір за специфікацією моделі
                                        </span>
                                    `}
                                </div>
                                <div style="margin-top:6px; display:flex; flex-direction:column; gap:4px;">

                                    ${item.alternatives.map((alt, aIdx) => `
                                        <label style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.05); padding:8px 10px; border-radius:6px; font-size:12px; cursor:pointer;">
                                            <div style="display:flex; align-items:center; gap:8px;">
                                                <input type="radio" name="item_${item.id}" value="${alt.brand}|${alt.part_number}|${alt.price}|${item.category_name}|${item.oem_number || ''}" ${aIdx === 0 ? 'checked' : ''}>
                                                <span>🔹 <strong>${escapeHtml(alt.brand)}</strong> (${escapeHtml(alt.part_number)})</span>
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
                <span>🗓️ ${formatDate(o.created_at)}</span>
                <span>Замовлення #${o.id}</span>
            </div>
            <div style="font-size:13px; font-weight:700;">🔧 Замінені запчастини:</div>
            <div style="font-size:12px; margin-top:2px; color:var(--text-main);">
                ${o.items.map(i => `<div>• ${escapeHtml(i.category_name)} (${escapeHtml(i.brand)} ${escapeHtml(i.part_number)})</div>`).join('')}
            </div>
        </div>
    `).join('');
}

function openReturnModal(orderId) {
    activeReturnOrderId = orderId;
    document.getElementById('returnOrderId').textContent = orderId;
    returnModal.style.display = 'flex';
}

function closeReturnModal() {
    returnModal.style.display = 'none';
}

async function openChatModal(requestId) {
    activeChatRequestId = requestId;
    document.getElementById('chatRequestId').textContent = requestId;
    chatModal.style.display = 'flex';
    await loadChatMessages(requestId);
}

function closeChatModal() {
    chatModal.style.display = 'none';
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

        showToast('🔁 Запит на повтор замовлення надіслано експерту!');
        await loadMyRequests(token);
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    }
}

function getStatusTitle(st) {
    const map = {
        'sent_to_preparation': '⏳ В підготовці',
        'assembling': '⚙️ Збирається у постачальників',
        'ready_for_shipping': '📸 Зібрано, готується до відправки',
        'shipped': '🚚 Відправлено Новою Поштою',
        'delivered': '✅ Отримано клієнтом'
    };
    return map[st] || st;
}

function getPaymentTitle(pm) {
    const map = {
        'cash_on_delivery': '🚚 Накладений платіж Нової Пошти',
        'fop_prepayment': '💳 Передплата на рахунок ФОП',
        'partial_prepayment': '⚖️ Часткова передплата'
    };
    return map[pm] || pm;
}

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
