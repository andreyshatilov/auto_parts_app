/**
 * Frontend JavaScript Logic: Панель Експертів "Міністерство Запчастин" (Українська версія)
 * 
 * Взаємодіє з REST API FastAPI: база авто, клієнти, вхідні запити,
 * конструктор кошторисів з АВТО-КРОСАМИ (за 5 мс без ШІ), замовлення, ТТН,
 * реєстр повернень, чат та ФІНАНСОВА АНАЛІТИКА P&L.
 */


const API_BASE_URL = window.location.origin.includes(':8000') || window.location.origin.includes('5500')
    ? 'http://localhost:8000/api/v1'
    : '/api/v1';

const HEALTH_CHECK_URL = `${API_BASE_URL}/health`;

// DOM Елементи
const addCarForm = document.getElementById('addCarForm');
const vinInput = document.getElementById('vinInput');
const vinCounter = document.getElementById('vinCounter');
const searchInput = document.getElementById('searchInput');
const searchClientsInput = document.getElementById('searchClientsInput');
const carsContainer = document.getElementById('carsContainer');
const clientsContainer = document.getElementById('clientsContainer');
const requestsQueueContainer = document.getElementById('requestsQueueContainer');
const ordersContainer = document.getElementById('ordersContainer');
const returnsContainer = document.getElementById('returnsContainer');
const carsCountEl = document.getElementById('carsCount');
const clientsCountEl = document.getElementById('clientsCount');
const pendingBadge = document.getElementById('pendingBadge');
const ordersBadge = document.getElementById('ordersBadge');
const returnsBadge = document.getElementById('returnsBadge');
const serverStatusDot = document.getElementById('serverStatusDot');
const serverStatusText = document.getElementById('serverStatusText');
const toastContainer = document.getElementById('toastContainer');
const submitBtn = document.getElementById('submitBtn');
const proposalModal = document.getElementById('proposalModal');
const proposalForm = document.getElementById('proposalForm');
const proposalItemsContainer = document.getElementById('proposalItemsContainer');
const orderStatusModal = document.getElementById('orderStatusModal');
const orderStatusForm = document.getElementById('orderStatusForm');
const adminChatModal = document.getElementById('adminChatModal');
const adminChatSendForm = document.getElementById('adminChatSendForm');
const adminChatMessagesContainer = document.getElementById('adminChatMessagesContainer');

let currentActiveRequestId = null;
let currentActiveOrderId = null;
let activeAdminChatRequestId = null;
let itemBlockCounter = 0;

document.addEventListener('DOMContentLoaded', () => {
    checkServerHealth();
    loadCars();
    loadClients();
    loadRequestsQueue();
    loadOrdersQueue();
    loadReturnsQueue();
    loadAnalyticsSummary();
    setupEventListeners();
});

function switchAdminTab(tabName) {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.admin-tab-content').forEach(c => c.classList.remove('active'));

    if (tabName === 'cars') {
        document.getElementById('tabCarsBtn').classList.add('active');
        document.getElementById('carsTabContent').classList.add('active');
    } else if (tabName === 'clients') {
        document.getElementById('tabClientsBtn').classList.add('active');
        document.getElementById('clientsTabContent').classList.add('active');
        loadClients();
    } else if (tabName === 'garages') {
        document.getElementById('tabGaragesBtn').classList.add('active');
        document.getElementById('garagesTabContent').classList.add('active');
        loadGarages();
    } else if (tabName === 'requests') {
        document.getElementById('tabRequestsBtn').classList.add('active');
        document.getElementById('requestsTabContent').classList.add('active');
        loadRequestsQueue();
    } else if (tabName === 'orders') {
        document.getElementById('tabOrdersBtn').classList.add('active');
        document.getElementById('ordersTabContent').classList.add('active');
        loadOrdersQueue();
    } else if (tabName === 'returns') {
        document.getElementById('tabReturnsBtn').classList.add('active');
        document.getElementById('returnsTabContent').classList.add('active');
        loadReturnsQueue();
    } else if (tabName === 'analytics') {
        document.getElementById('tabAnalyticsBtn').classList.add('active');
        document.getElementById('analyticsTabContent').classList.add('active');
        loadAnalyticsSummary();
    }
}

function setupEventListeners() {
    vinInput.addEventListener('input', async (e) => {
        let value = e.target.value.replace(/\s+/g, '').toUpperCase();
        e.target.value = value;
        vinCounter.textContent = `${value.length}/17`;

        if (value.length >= 3) {
            try {
                const res = await fetch(`${API_BASE_URL}/vin/decode?vin=${value}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.is_decoded && data.brand) {
                        const brandField = document.getElementById('brandInput');
                        if (!brandField.value) {
                            brandField.value = data.brand;
                            showToast(`⚡ Декодер VIN: Визначено марку ${data.brand} (${data.country})`);
                        }
                    }
                }
            } catch (err) {
                console.error(err);
            }
        }
    });


    addCarForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleAddCar();
    });

    proposalForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleProposalSubmit();
    });

    orderStatusForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleOrderStatusSubmit();
    });

    adminChatSendForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!activeAdminChatRequestId) return;
        const msg = document.getElementById('adminChatInput').value.trim();

        try {
            const res = await fetch(`${API_BASE_URL}/chat/messages?sender_type=manager`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ request_id: activeAdminChatRequestId, message: msg })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Помилка');

            document.getElementById('adminChatInput').value = '';
            await loadAdminChatMessages(activeAdminChatRequestId);
        } catch (err) {
            showToast(`❌ ${err.message}`, 'error');
        }
    });

    let searchTimeout = null;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => loadCars(e.target.value.trim()), 300);
    });

    let searchClientsTimeout = null;
    searchClientsInput.addEventListener('input', (e) => {
        clearTimeout(searchClientsTimeout);
        searchClientsTimeout = setTimeout(() => loadClients(e.target.value.trim()), 300);
    });
}

async function checkServerHealth() {
    try {
        const res = await fetch(HEALTH_CHECK_URL);
        if (res.ok) {
            const data = await res.json();
            if (data.status === 'online') {
                serverStatusDot.className = 'status-indicator online';
                serverStatusText.textContent = '🟢 Сервер Онлайн (Render + PostgreSQL)';
            } else throw new Error();
        } else throw new Error();
    } catch {
        serverStatusDot.className = 'status-indicator offline';
        serverStatusText.textContent = '🔴 Сервер недоступний';
    }
}

async function loadCars(searchQuery = '') {
    try {
        let url = `${API_BASE_URL}/cars/`;
        if (searchQuery) url += `?search=${encodeURIComponent(searchQuery)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error();
        const cars = await res.json();
        renderCars(cars);
    } catch (err) {
        carsContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--danger); padding: 20px;">⚠️ Помилка завантаження авто</div>`;
    }
}

function renderCars(cars) {
    carsCountEl.textContent = cars.length;
    if (cars.length === 0) {
        carsContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted); padding: 20px;">🚗 База авто порожня.</div>`;
        return;
    }

    carsContainer.innerHTML = cars.map(car => `
        <div class="car-card">
            <div class="car-header-row">
                <div>
                    <div class="car-title">${escapeHtml(car.brand)} ${escapeHtml(car.model)} ${car.release_date ? `(${escapeHtml(car.release_date)} р.в.)` : ''}</div>
                    <div class="car-modification">${escapeHtml(car.modification || 'Без модифікації')}</div>
                </div>
            </div>
            <div class="vin-badge">
                <span>VIN: ${escapeHtml(car.vin)}</span>
                <button class="copy-vin-btn" onclick="copyToClipboard('${car.vin}')">📋</button>
            </div>
            <div class="car-details-grid">
                <div class="detail-item"><span class="detail-label">Рік випуску</span><span class="detail-value">${escapeHtml(car.release_date || '—')}</span></div>
                <div class="detail-item"><span class="detail-label">Двигун</span><span class="detail-value">${escapeHtml(car.engine_code || '—')}</span></div>
                <div class="detail-item"><span class="detail-label">КПП</span><span class="detail-value">${escapeHtml(car.transmission_type || '—')}</span></div>
            </div>
            <div class="car-footer">
                <span>ID: #${car.id} | ${car.client_id ? `Власник #${car.client_id}` : 'Без власника'}</span>
                <button class="btn-delete" onclick="deleteCar(${car.id}, '${car.vin}')">Видалити</button>
            </div>
        </div>
    `).join('');
}

async function loadClients(searchQuery = '') {
    try {
        let url = `${API_BASE_URL}/clients/`;
        if (searchQuery) url += `?search=${encodeURIComponent(searchQuery)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error();
        const clients = await res.json();
        renderClients(clients);
    } catch (err) {
        clientsContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--danger); padding: 20px;">⚠️ Помилка клієнтів</div>`;
    }
}

function renderClients(clients) {
    clientsCountEl.textContent = clients.length;

    // Populate adminClientSelect dropdown for Add Car form
    const adminClientSelect = document.getElementById('adminClientSelect');
    if (adminClientSelect) {
        const currentVal = adminClientSelect.value;
        adminClientSelect.innerHTML = '<option value="">Без прив\'язки (Загальний реєстр авто)</option>';
        clients.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = `👤 ${c.first_name} ${c.last_name} (${c.phone})`;
            adminClientSelect.appendChild(opt);
        });
        if (currentVal) adminClientSelect.value = currentVal;
    }

    if (clients.length === 0) {
        clientsContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted); padding: 20px;">Клієнтів немає.</div>`;
        return;
    }

    clientsContainer.innerHTML = clients.map(c => `
        <div class="client-card">
            <div class="car-header-row">
                <div>
                    <div class="car-title">👤 ${escapeHtml(c.first_name)} ${escapeHtml(c.last_name)} (ID #${c.id})</div>
                    <div class="car-modification">📞 ${escapeHtml(c.phone)}</div>
                </div>
                <button class="btn btn-secondary" style="font-size:11px; padding:4px 8px;" onclick="prefillAddCarForClient(${c.id}, '${escapeHtml(c.first_name)} ${escapeHtml(c.last_name)}')">
                    ➕ Додати авто в гараж
                </button>
            </div>
            <div class="car-details-grid">
                <div class="detail-item" style="grid-column: 1/-1;"><span class="detail-label">Нова Пошта</span><span class="detail-value">${escapeHtml(c.shipping_address || 'Не вказано')}</span></div>
            </div>
            <div style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; font-size: 12px; margin-top: 6px;">
                <strong>Гараж (${c.cars.length} авто):</strong>
                ${c.cars.length > 0 ? c.cars.map(car => `<div style="margin-top:2px; color:#60a5fa;">• ${escapeHtml(car.brand)} ${escapeHtml(car.model)} ${car.release_date ? `(${car.release_date} р.в.)` : ''} (VIN: ${escapeHtml(car.vin)})</div>`).join('') : '<div style="color:var(--text-muted);">Порожній</div>'}
            </div>
        </div>
    `).join('');
}

async function loadRequestsQueue() {
    try {
        const res = await fetch(`${API_BASE_URL}/requests/`);
        if (!res.ok) throw new Error();
        const requests = await res.json();
        const pending = requests.filter(r => r.status === 'sent');
        pendingBadge.textContent = pending.length;
        renderRequestsQueue(requests);
    } catch (err) {
        requestsQueueContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--danger); padding: 20px;">⚠️ Помилка запитів</div>`;
    }
}

function renderRequestsQueue(requests) {
    if (requests.length === 0) {
        requestsQueueContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted); padding: 20px;">📥 Запитів немає.</div>`;
        return;
    }

    requestsQueueContainer.innerHTML = requests.map(req => `
        <div class="car-card">
            <div class="car-header-row">
                <div>
                    <div class="car-title">Запит #${req.id}</div>
                    <div class="car-modification">Від ${formatDate(req.created_at)}</div>
                </div>
                <span class="badge ${req.status === 'completed' ? 'badge-engine' : 'badge-trans'}">
                    ${req.status === 'completed' ? '✓ Оброблено' : '⏳ Очікує кошторису'}
                </span>
            </div>

            <div style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3); padding: 10px; border-radius: 8px; font-size: 13px;">
                <strong>🚗 Автомобіль:</strong> ${req.car ? `${escapeHtml(req.car.brand)} ${escapeHtml(req.car.model)} ${req.car.release_date ? `(${escapeHtml(req.car.release_date)} р.в.)` : ''} | VIN: ${escapeHtml(req.car.vin)} | Двигун: ${escapeHtml(req.car.engine_code || '—')}` : 'Невідомо'}
            </div>

            <div style="font-size: 14px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; font-weight: 500;">
                💬 "${escapeHtml(req.client_message)}"
            </div>

            <div class="car-footer">
                <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="openAdminChatModal(${req.id})">
                    💬 Чат з клієнтом
                </button>
                ${req.status !== 'completed' ? `
                    <button class="btn btn-primary" style="padding: 6px 12px; width: auto; font-size: 12px;" onclick="openProposalModal(${req.id}, '${escapeHtml(req.car ? req.car.brand + ' ' + req.car.model : '')}')">
                        📝 Скласти кошторис
                    </button>
                ` : '<span style="color:#34d399; font-weight:600;">✓ Кошторис надіслано</span>'}
            </div>
        </div>
    `).join('');
}

async function loadOrdersQueue() {
    try {
        const res = await fetch(`${API_BASE_URL}/orders/`);
        if (!res.ok) throw new Error();
        const orders = await res.json();
        ordersBadge.textContent = orders.length;
        renderOrdersQueue(orders);
    } catch (err) {
        ordersContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--danger); padding: 20px;">⚠️ Помилка замовлень</div>`;
    }
}

function renderOrdersQueue(orders) {
    if (orders.length === 0) {
        ordersContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted); padding: 20px;">📦 Замовлень у роботі поки немає.</div>`;
        return;
    }

    ordersContainer.innerHTML = orders.map(order => `
        <div class="car-card">
            <div class="car-header-row">
                <div>
                    <div class="car-title">Замовлення #${order.id}</div>
                    <div class="car-modification">Від ${formatDate(order.created_at)}</div>
                </div>
                <span class="badge ${order.status === 'shipped' ? 'badge-engine' : 'badge-trans'}">
                    ${getStatusTitle(order.status)}
                </span>
            </div>

            <div style="font-size: 15px; font-weight: 700; color: #34d399;">
                Продаж: ${order.total_price} грн ${order.purchase_cost ? `<small style="color:var(--text-muted); font-weight:400;">(Закупівля: ${order.purchase_cost} грн | Прибуток: ${(order.total_price - order.purchase_cost).toFixed(2)} грн)</small>` : ''}
            </div>

            <div style="font-size: 12px; background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;">
                <strong>Доставка НП:</strong> ${escapeHtml(order.shipping_address || 'Не вказано')}
                ${order.ttn_number ? `<div style="color:#60a5fa; margin-top:2px;">📦 ТТН: ${escapeHtml(order.ttn_number)}</div>` : ''}
            </div>

            <div style="font-size:12px;">
                <strong>Обрані деталі:</strong>
                ${order.items.map(i => `<div style="color:var(--text-muted);">• ${escapeHtml(i.category_name)}: ${escapeHtml(i.brand)} ${escapeHtml(i.part_number)} (${i.price} грн)</div>`).join('')}
            </div>

            <div class="car-footer">
                <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="printOrderPackingSlip(${order.id}, '${escapeHtml(order.shipping_address || '')}', '${escapeHtml(order.total_price)}')">
                    🖨️ Друк чек-листа
                </button>
                <button class="btn btn-primary" style="padding: 6px 12px; width: auto; font-size: 12px;" onclick="openOrderStatusModal(${order.id}, '${order.status}', '${escapeHtml(order.assembly_photo_url || '')}', '${escapeHtml(order.ttn_number || '')}', '${order.purchase_cost || ''}')">
                    ⚙️ Статус / ТТН
                </button>
            </div>
        </div>
    `).join('');
}

async function loadReturnsQueue() {
    try {
        const res = await fetch(`${API_BASE_URL}/returns/`);
        if (!res.ok) throw new Error();
        const returnsList = await res.json();
        returnsBadge.textContent = returnsList.filter(r => r.status === 'requested').length;
        renderReturnsQueue(returnsList);
    } catch (err) {
        returnsContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--danger); padding: 20px;">⚠️ Помилка повернень</div>`;
    }
}

function renderReturnsQueue(returnsList) {
    if (returnsList.length === 0) {
        returnsContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted); padding: 20px;">🔄 Заявок на повернення немає.</div>`;
        return;
    }

    returnsContainer.innerHTML = returnsList.map(ret => `
        <div class="car-card">
            <div class="car-header-row">
                <div>
                    <div class="car-title">Заявка на повернення #${ret.id}</div>
                    <div class="car-modification">Замовлення #${ret.order_id} • ${formatDate(ret.created_at)}</div>
                </div>
                <span class="badge ${ret.status === 'approved' ? 'badge-engine' : 'badge-trans'}">
                    ${ret.status === 'requested' ? '⏳ На розгляді' : (ret.status === 'approved' ? '✓ Схвалено' : '✕ Відхилено')}
                </span>
            </div>

            <div style="font-size:13px; background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); padding:10px; border-radius:8px;">
                <strong>Причина:</strong> "${escapeHtml(ret.reason)}"
                <div style="font-size:11px; color:var(--text-muted); margin-top:4px;">Тип: ${ret.return_type}</div>
            </div>

            ${ret.status === 'requested' ? `
                <div class="car-footer" style="gap:8px;">
                    <button class="btn btn-primary" style="padding:6px; font-size:12px; flex:1;" onclick="updateReturnStatus(${ret.id}, 'approved')">✓ Схвалити повернення</button>
                    <button class="btn btn-delete" style="padding:6px; font-size:12px; flex:1;" onclick="updateReturnStatus(${ret.id}, 'rejected')">✕ Відхилити</button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

async function updateReturnStatus(returnId, statusVal) {
    try {
        const res = await fetch(`${API_BASE_URL}/returns/${returnId}/status?status_val=${statusVal}`, { method: 'PUT' });
        if (!res.ok) throw new Error();
        showToast('✅ Статус повернення оновлено!');
        await loadReturnsQueue();
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    }
}

/**
 * Завантаження Фінансової Аналітики P&L
 */
async function loadAnalyticsSummary() {
    try {
        const res = await fetch(`${API_BASE_URL}/analytics/summary`);
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('valTotalRevenue').textContent = `${data.total_revenue_uah.toFixed(2)} грн`;
        document.getElementById('valTotalCost').textContent = `${data.total_purchase_cost_uah.toFixed(2)} грн`;
        document.getElementById('valNetProfit').textContent = `${data.net_profit_uah.toFixed(2)} грн (${data.margin_percent}%)`;
        document.getElementById('valAvgOrder').textContent = `${data.avg_order_value_uah.toFixed(2)} грн`;

        const topContainer = document.getElementById('topClientsContainer');
        if (data.top_clients.length === 0) {
            topContainer.innerHTML = `<div style="color:var(--text-muted); font-size:13px;">Немає виконаних замовлень уперіоді.</div>`;
        } else {
            topContainer.innerHTML = data.top_clients.map((c, i) => `
                <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px;">
                    <span>🥇 ${i+1}. <strong>${escapeHtml(c.name)}</strong> (${escapeHtml(c.phone)}) — ${c.orders_count} замовлень</span>
                    <span style="color:#34d399; font-weight:700;">${c.total_spent} грн</span>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error(err);
    }
}

function printOrderPackingSlip(orderId, address, total) {
    const printWin = window.open('', '_blank');
    printWin.document.write(`
        <html>
        <head>
            <title>Чек-лист Збірки Замовлення #${orderId}</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; color: #000; }
                h1 { font-size: 20px; margin-bottom: 5px; }
                .border { border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 15px; }
                .box { border: 1px solid #000; padding: 10px; margin-bottom: 15px; }
            </style>
        </head>
        <body>
            <h1>🏛️ Міністерство Запчастин — Чек-лист Комплектації Замовлення #${orderId}</h1>

            <div class="border">Дата формування: ${new Date().toLocaleDateString('uk-UA')}</div>

            <div class="box">
                <strong>Отримувач та Нова Пошта:</strong><br>
                ${address || 'Не вказано'}
            </div>

            <div class="box">
                <strong>Сума до сплати (Накладений платіж):</strong> ${total} грн
            </div>

            <div style="margin-top:40px; font-size:12px;">Подпис комплектувальника: __________________</div>
            <script>window.print();</script>
        </body>
        </html>
    `);
    printWin.document.close();
}

/**
 * АВТО-ПОШУК КРОСІВ при введенні OE номера у Конструкторі Кошторису (за 5 мс без ШІ)
 */
async function lookupCrossesForOE(blockId, oemInput) {
    const cleanOem = oemInput.value.trim();
    if (cleanOem.length < 3) return;

    try {
        const res = await fetch(`${API_BASE_URL}/crosses/search?oem=${encodeURIComponent(cleanOem)}`);
        if (!res.ok) return;
        const matches = await res.json();

        if (matches.length > 0) {
            const block = document.getElementById(blockId);
            const altsContainer = block.querySelector('.alts-container');

            // Очищаємо першу пусту строчку та заповнюємо знайденими з бази знань кросами
            altsContainer.innerHTML = matches.map(m => `
                <div class="alt-row" style="display:grid; grid-template-columns: 1fr 1fr 100px; gap:8px;">
                    <input type="text" class="alt-brand" value="${escapeHtml(m.brand)}" required>
                    <input type="text" class="alt-code" value="${escapeHtml(m.part_number)}" required>
                    <input type="number" class="alt-price" value="${m.price}" required>
                </div>
            `).join('');

            showToast(`⚡ База знань: підтягнуто ${matches.length} аналогів за 5 мс!`);
        }
    } catch (err) {
        console.error(err);
    }
}

function openProposalModal(requestId, carTitle) {
    currentActiveRequestId = requestId;
    document.getElementById('modalRequestId').textContent = requestId;
    document.getElementById('modalCarTitle').textContent = carTitle;
    proposalItemsContainer.innerHTML = '';
    itemBlockCounter = 0;
    addProposalItemBlock();
    proposalModal.style.display = 'flex';
}

function closeProposalModal() {
    proposalModal.style.display = 'none';
}

function addProposalItemBlock() {
    itemBlockCounter++;
    const blockId = `item-block-${itemBlockCounter}`;

    const block = document.createElement('div');
    block.className = 'card';
    block.id = blockId;
    block.style.background = 'rgba(15,23,42,0.8)';
    block.style.padding = '14px';

    block.innerHTML = `
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <strong>📦 Деталь #${itemBlockCounter}</strong>
            <button type="button" onclick="document.getElementById('${blockId}').remove()" style="background:none; border:none; color:#f87171; cursor:pointer;">Видалити</button>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Назва запчастини *</label>
                <input type="text" class="item-cat-input" placeholder="наприклад: Масляний фільтр" required>
            </div>
            <div class="form-group">
                <label>Оригінальний номер (OE) <span style="color:#60a5fa; font-size:10px;">(Авто-крос за 5 мс)</span></label>
                <input type="text" class="item-oe-input" placeholder="наприклад: 11427953129" onchange="lookupCrossesForOE('${blockId}', this)">
            </div>
        </div>
        <div style="margin-top: 8px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <label style="font-size:11px; color:var(--text-muted);">ВАРИАНТИ АНАЛОГІВ (БРЕНД / АРТИКУЛ / ЦІНА ГРН):</label>
                <button type="button" style="background:none; border:none; color:#60a5fa; font-size:11px; cursor:pointer;" onclick="addAltRowToBlock('${blockId}')">➕ Ще аналог</button>
            </div>
            <div class="alts-container" style="display:flex; flex-direction:column; gap:6px;">
                <div class="alt-row" style="display:grid; grid-template-columns: 1fr 1fr 100px; gap:8px;">
                    <input type="text" class="alt-brand" placeholder="Бренд (Knecht)" required>
                    <input type="text" class="alt-code" placeholder="Артикул (OX387D)" required>
                    <input type="number" class="alt-price" placeholder="Ціна грн" required>
                </div>
            </div>
        </div>
    `;

    proposalItemsContainer.appendChild(block);
}

function addAltRowToBlock(blockId) {
    const block = document.getElementById(blockId);
    const altsContainer = block.querySelector('.alts-container');
    const row = document.createElement('div');
    row.className = 'alt-row';
    row.style.display = 'grid';
    row.style.gridTemplateColumns = '1fr 1fr 100px';
    row.style.gap = '8px';
    row.innerHTML = `
        <input type="text" class="alt-brand" placeholder="Бренд" required>
        <input type="text" class="alt-code" placeholder="Артикул" required>
        <input type="number" class="alt-price" placeholder="Ціна грн" required>
    `;
    altsContainer.appendChild(row);
}

async function handleProposalSubmit() {
    if (!currentActiveRequestId) return;
    const items = [];
    const itemBlocks = proposalItemsContainer.querySelectorAll('.card');

    itemBlocks.forEach(block => {
        const cat = block.querySelector('.item-cat-input').value.trim();
        const oe = block.querySelector('.item-oe-input').value.trim() || null;

        const alts = [];
        const altRows = block.querySelectorAll('.alt-row');
        altRows.forEach(row => {
            const brand = row.querySelector('.alt-brand').value.trim();
            const code = row.querySelector('.alt-code').value.trim();
            const price = parseFloat(row.querySelector('.alt-price').value);

            if (brand && code && price) {
                alts.push({ brand, part_number: code, price, delivery_term: "1-2 дні" });
            }
        });

        if (cat && alts.length > 0) {
            items.push({ category_name: cat, oem_number: oe, alternatives: alts });
        }
    });

    if (items.length === 0) {
        showToast('⚠️ Заповніть хоча б одну деталь з аналогом!', 'error');
        return;
    }

    const payload = {
        request_id: currentActiveRequestId,
        manager_comment: document.getElementById('managerCommentInput').value.trim() || null,
        items
    };

    try {
        const res = await fetch(`${API_BASE_URL}/proposals/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Помилка');

        showToast('✅ Кошторис надіслано клієнту!');
        closeProposalModal();
        await loadRequestsQueue();
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    }
}

async function handleAddCar() {
    const clientIdVal = document.getElementById('adminClientSelect')?.value;

    const carData = {
        vin: vinInput.value.trim(),
        brand: document.getElementById('brandInput').value.trim(),
        model: document.getElementById('modelInput').value.trim(),
        modification: document.getElementById('modificationInput').value.trim() || null,
        release_date: document.getElementById('releaseDateInput').value.trim() || null,
        engine_code: document.getElementById('engineCodeInput').value.trim() || null,
        drive_type: document.getElementById('driveTypeSelect').value || null,
        transmission_type: document.getElementById('transmissionTypeSelect').value || null,
        transmission_code: document.getElementById('transmissionCodeInput').value.trim() || null,
        notes: document.getElementById('notesInput').value.trim() || null
    };

    if (clientIdVal) {
        carData.client_id = parseInt(clientIdVal);
    }

    submitBtn.disabled = true;
    try {
        const res = await fetch(`${API_BASE_URL}/cars/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(carData)
        });
        const result = await res.json();
        if (!res.ok) throw new Error(result.detail || 'Помилка');

        showToast(`✅ Автомобіль ${result.brand} ${result.model} збережено!`);
        addCarForm.reset();
        vinCounter.textContent = '0/17';
        await loadCars();
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
    }
}

async function openAdminChatModal(requestId) {
    activeAdminChatRequestId = requestId;
    document.getElementById('adminChatRequestId').textContent = requestId;
    adminChatModal.style.display = 'flex';
    await loadAdminChatMessages(requestId);
}

function closeAdminChatModal() {
    adminChatModal.style.display = 'none';
}

async function loadAdminChatMessages(requestId) {
    try {
        const res = await fetch(`${API_BASE_URL}/chat/messages/${requestId}`);
        if (!res.ok) return;
        const messages = await res.json();
        adminChatMessagesContainer.innerHTML = messages.map(m => `
            <div style="align-self: ${m.sender_type === 'manager' ? 'flex-end' : 'flex-start'}; background: ${m.sender_type === 'manager' ? 'rgba(59,130,246,0.3)' : 'rgba(255,255,255,0.1)'}; padding:8px 12px; border-radius:10px; max-width:80%; font-size:13px;">
                <div style="font-size:10px; color:var(--text-muted);">${m.sender_type === 'manager' ? 'Ви (Експерт)' : 'Клієнт'} • ${formatDate(m.created_at)}</div>
                <div>${escapeHtml(m.message)}</div>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

function openOrderStatusModal(orderId, currentStatus, photoUrl, ttn, purchaseCost) {
    currentActiveOrderId = orderId;
    document.getElementById('modalOrderId').textContent = orderId;
    document.getElementById('orderStatusSelect').value = currentStatus || 'sent_to_preparation';
    document.getElementById('orderPhotoInput').value = photoUrl || '';
    document.getElementById('orderTtnInput').value = ttn || '';
    document.getElementById('orderPurchaseCostInput').value = purchaseCost || '';
    orderStatusModal.style.display = 'flex';
}

function closeOrderStatusModal() {
    orderStatusModal.style.display = 'none';
}

async function handleOrderStatusSubmit() {
    if (!currentActiveOrderId) return;
    const payload = {
        status: document.getElementById('orderStatusSelect').value,
        assembly_photo_url: document.getElementById('orderPhotoInput').value.trim() || null,
        ttn_number: document.getElementById('orderTtnInput').value.trim() || null,
        purchase_cost: parseFloat(document.getElementById('orderPurchaseCostInput').value) || null
    };

    try {
        const res = await fetch(`${API_BASE_URL}/orders/${currentActiveOrderId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Помилка');

        showToast(`✅ Замовлення #${currentActiveOrderId} оновлено!`);
        closeOrderStatusModal();
        await loadOrdersQueue();
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    }
}

async function deleteCar(carId, vin) {
    if (!confirm(`Видалити авто VIN: ${vin}?`)) return;
    try {
        const res = await fetch(`${API_BASE_URL}/cars/${carId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Помилка');
        showToast(`🗑️ Авто з VIN ${vin} видалено`);
        await loadCars();
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => showToast(`📋 VIN скопійовано: ${text}`));
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

function showToast(msg, type = 'success') {
    const t = document.createElement('div');
    t.className = `toast ${type}`;
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

async function loadGarages(searchQuery = '') {
    const garagesContainer = document.getElementById('garagesContainer');
    const garagesBadge = document.getElementById('garagesBadge');
    if (!garagesContainer) return;

    try {
        let url = `${API_BASE_URL}/clients/`;
        if (searchQuery) url += `?search=${encodeURIComponent(searchQuery)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error();
        const clients = await res.json();

        let totalCarsCount = 0;
        let allGaragesHtml = '';

        clients.forEach(client => {
            const clientCars = client.cars || [];
            totalCarsCount += clientCars.length;

            if (clientCars.length > 0) {
                clientCars.forEach(car => {
                    allGaragesHtml += `
                        <div class="car-card" style="border-left: 4px solid #3b82f6;">
                            <div class="car-header-row">
                                <div>
                                    <div class="car-title">${escapeHtml(car.brand)} ${escapeHtml(car.model)} ${car.release_date ? `(${escapeHtml(car.release_date)} р.в.)` : ''}</div>
                                    <div class="car-modification">${escapeHtml(car.modification || 'Без специфікації кузова')}</div>
                                </div>
                                <button class="btn btn-secondary" style="font-size:11px; padding:4px 8px;" onclick="prefillAddCarForClient(${client.id}, '${escapeHtml(client.first_name)} ${escapeHtml(client.last_name)}')">
                                    ➕ Додати авто клієнту
                                </button>
                            </div>
                            
                            <div class="vin-badge" style="background: rgba(59,130,246,0.15); border-color: rgba(59,130,246,0.3);">
                                <span>VIN: <strong>${escapeHtml(car.vin)}</strong></span>
                                <button class="copy-vin-btn" onclick="copyToClipboard('${car.vin}')">📋</button>
                            </div>

                            <div style="background: rgba(15,23,42,0.6); padding: 8px 10px; border-radius: 8px; font-size: 12px; margin-top: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <div style="color: #60a5fa; font-weight: 700;">👤 Власник: ${escapeHtml(client.first_name)} ${escapeHtml(client.last_name)} (ID #${client.id})</div>
                                <div>📞 Телефон: <strong>${escapeHtml(client.phone)}</strong></div>
                                ${client.email ? `<div>✉️ Email: ${escapeHtml(client.email)}</div>` : ''}
                                <div>📦 Доставка НП: ${escapeHtml(client.shipping_address || 'Не вказано')}</div>
                            </div>

                            <div class="car-details-grid" style="margin-top: 8px;">
                                <div class="detail-item"><span class="detail-label">Двигун</span><span class="detail-value">${escapeHtml(car.engine_code || '—')}</span></div>
                                <div class="detail-item"><span class="detail-label">КПП</span><span class="detail-value">${escapeHtml(car.transmission_type || '—')}</span></div>
                                <div class="detail-item"><span class="detail-label">Привід</span><span class="detail-value">${escapeHtml(car.drive_type || '—')}</span></div>
                            </div>

                            <div class="car-footer" style="margin-top: 8px;">
                                <span style="font-size:11px; color:var(--text-muted);">Додано: ${formatDate(car.created_at)}</span>
                                <button class="btn-delete" onclick="deleteCar(${car.id}, '${car.vin}')">Видалити</button>
                            </div>
                        </div>
                    `;
                });
            }
        });

        if (garagesBadge) garagesBadge.textContent = totalCarsCount;

        if (totalCarsCount === 0) {
            garagesContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted); padding: 20px;">Жодного авто в гаражах клієнтів не знайдено.</div>`;
        } else {
            garagesContainer.innerHTML = allGaragesHtml;
        }

        const searchGaragesInput = document.getElementById('searchGaragesInput');
        if (searchGaragesInput && !searchGaragesInput.dataset.listener) {
            searchGaragesInput.dataset.listener = 'true';
            let timeout = null;
            searchGaragesInput.addEventListener('input', (e) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => loadGarages(e.target.value.trim()), 300);
            });
        }
    } catch (err) {
        console.error(err);
        garagesContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--danger); padding: 20px;">⚠️ Помилка завантаження гаражів</div>`;
    }
}

function prefillAddCarForClient(clientId, clientName) {
    switchAdminTab('cars');
    const select = document.getElementById('adminClientSelect');
    if (select) select.value = clientId;
    showToast(`📝 Обрано клієнта ${clientName}. Введіть VIN-код для додавання авто в його гараж!`);
    const vinInp = document.getElementById('vinInput');
    if (vinInp) vinInp.focus();
}
