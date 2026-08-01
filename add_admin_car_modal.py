import re

html_modal = """
    <!-- Admin Car Detail Modal -->
    <div id="adminCarDetailModal" class="modal-backdrop" style="display: none; align-items:center; justify-content:center; padding:16px;">
        <div class="modal-content" style="max-width: 500px; width: 100%; max-height:90vh; overflow-y:auto; background: #0f172a; border: 1px solid rgba(255,255,255,0.1); border-radius:12px; padding:20px; color:white;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
                <div>
                    <h2 id="adminDetailCarTitle" style="margin:0; font-size: 20px; color: #60a5fa;">Car Title</h2>
                    <div id="adminDetailCarVin" style="font-family: monospace; font-size: 14px; margin-top: 4px; color: #94a3b8;">VIN: ---</div>
                </div>
                <button onclick="closeAdminCarDetailModal()" style="background:none; border:none; color:white; font-size:24px; cursor:pointer;">&times;</button>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 13px;">
                <div><span style="color:#94a3b8; display:block; font-size:11px;">РІК ВИПУСКУ</span><strong id="adminDetailCarYear">---</strong></div>
                <div><span style="color:#94a3b8; display:block; font-size:11px;">ПОКОЛІННЯ / КУЗОВ</span><strong id="adminDetailCarGen">---</strong></div>
                
                <div><span style="color:#94a3b8; display:block; font-size:11px;">ДВИГУН</span><strong id="adminDetailCarEngine">---</strong></div>
                <div><span style="color:#94a3b8; display:block; font-size:11px;">ПАЛЬНЕ</span><strong id="adminDetailCarFuel">---</strong></div>
                
                <div><span style="color:#94a3b8; display:block; font-size:11px;">ТРАНСМІСІЯ</span><strong id="adminDetailCarTrans">---</strong></div>
                <div><span style="color:#94a3b8; display:block; font-size:11px;">ПРИВІД</span><strong id="adminDetailCarDrive">---</strong></div>
                
                <div><span style="color:#94a3b8; display:block; font-size:11px;">ПОТУЖНІСТЬ</span><strong id="adminDetailCarHp">---</strong></div>
                <div><span style="color:#94a3b8; display:block; font-size:11px;">КОЛІР</span><strong id="adminDetailCarColor">---</strong></div>
                
                <div><span style="color:#94a3b8; display:block; font-size:11px;">ЗАВОД</span><strong id="adminDetailCarPlant">---</strong></div>
                <div><span style="color:#94a3b8; display:block; font-size:11px;">ПРОБІГ</span><strong id="adminDetailCarMileage">---</strong></div>
            </div>

            <div id="adminDetailCarNotesContainer" style="margin-top:16px; display:none;">
                <span style="color:#94a3b8; display:block; font-size:11px; margin-bottom:4px;">НОТАТКИ КЛІЄНТА</span>
                <div id="adminDetailCarNotes" style="background: rgba(255,255,255,0.05); padding:8px; border-radius:6px; font-size:12px;"></div>
            </div>

            <div style="margin-top:16px; border-top:1px solid rgba(255,255,255,0.1); padding-top:16px;">
                <img id="adminDetailCarPhoto" src="" style="width:100%; border-radius:8px; display:none;">
            </div>
            
            <button class="btn btn-primary" style="width:100%; margin-top:16px; padding:10px;" onclick="closeAdminCarDetailModal()">Закрити</button>
        </div>
    </div>
"""

js_modal = """
let adminCarsCache = [];

function setAdminCarsCache(cars) {
    adminCarsCache = cars;
}

window.openAdminCarDetailModal = async function(carId) {
    let car = adminCarsCache.find(c => c.id === carId);
    
    // If not found in cache, we could fetch it, but usually it is in cache because we just clicked it
    if (!car) {
        try {
            const res = await fetch(`${API_BASE_URL}/cars/` + carId, {
                headers: { 'X-Admin-Token': localStorage.getItem(ADMIN_TOKEN_KEY) }
            });
            if (res.ok) {
                car = await res.json();
            }
        } catch (e) {}
    }

    if (!car) {
        showToast('Авто не знайдено', 'error');
        return;
    }

    document.getElementById('adminDetailCarTitle').textContent = `${car.brand} ${car.model}`;
    document.getElementById('adminDetailCarVin').textContent = `VIN: ${car.vin || 'Немає'}`;
    
    document.getElementById('adminDetailCarYear').textContent = car.release_date || '-';
    
    const genBody = [car.generation, car.body_type].filter(Boolean).join(' / ');
    document.getElementById('adminDetailCarGen').textContent = genBody || '-';
    
    document.getElementById('adminDetailCarEngine').textContent = car.engine_code || '-';
    document.getElementById('adminDetailCarFuel').textContent = car.fuel_type || '-';
    document.getElementById('adminDetailCarTrans').textContent = `${car.transmission_type || '-'} ${car.transmission_code ? '('+car.transmission_code+')' : ''}`;
    document.getElementById('adminDetailCarDrive').textContent = car.drive_type || '-';
    document.getElementById('adminDetailCarHp').textContent = car.horse_power ? `${car.horse_power} к.с.` : '-';
    document.getElementById('adminDetailCarColor').textContent = car.color_code || '-';
    document.getElementById('adminDetailCarPlant').textContent = car.assembly_plant || '-';
    document.getElementById('adminDetailCarMileage').textContent = car.mileage ? `${car.mileage.toLocaleString('uk-UA')} км` : '-';
    
    const notesContainer = document.getElementById('adminDetailCarNotesContainer');
    if (car.notes) {
        notesContainer.style.display = 'block';
        document.getElementById('adminDetailCarNotes').textContent = car.notes;
    } else {
        notesContainer.style.display = 'none';
    }

    const photoImg = document.getElementById('adminDetailCarPhoto');
    if (car.custom_photo_url) {
        photoImg.src = car.custom_photo_url;
        photoImg.style.display = 'block';
    } else {
        photoImg.style.display = 'none';
    }

    const modal = document.getElementById('adminCarDetailModal');
    modal.style.display = 'flex';
};

window.closeAdminCarDetailModal = function() {
    document.getElementById('adminCarDetailModal').style.display = 'none';
};
"""

# Update index.html
with open('admin_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

if 'id="adminCarDetailModal"' not in html:
    html = html.replace('</body>', html_modal + '\n</body>')
    with open('admin_frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

# Update app.js
with open('admin_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

if 'openAdminCarDetailModal' not in js:
    js += '\n' + js_modal

# Now we need to inject setAdminCarsCache and add the button to renderCars and client cars
js = js.replace('function renderCars(cars) {', 'function renderCars(cars) {\n    setAdminCarsCache(cars);')
js = js.replace('const carsListHTML = client.cars.map(car => {', 'setAdminCarsCache(client.cars);\n                const carsListHTML = client.cars.map(car => {')

# Add 'Огляд' button
btn_html = r'<button class="btn btn-secondary" style="font-size:11px; padding:4px 8px; margin-right:4px;" onclick="openAdminCarDetailModal(${car.id})">Огляд</button>'

# For renderCars:
js = js.replace(
    '''<button class="btn-delete" onclick="deleteCar(${car.id}, '${car.vin}')">Видалити</button>''',
    btn_html + '''\n                <button class="btn-delete" onclick="deleteCar(${car.id}, '${car.vin}')">Видалити</button>'''
)


with open('admin_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Admin car details feature added successfully!")
