const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '../client_frontend/app.js');
let js = fs.readFileSync(filePath, 'utf-8');

const subCatalogCode = `

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
    
    const listHtml = cat.items.map(item => \`
        <div class="card parts-cat-card" style="margin-bottom: 8px;" onclick="addPartFromSubCatalog('\${item.name}')">
            <div class="cat-info" style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                <div class="cat-text">
                    <span class="cat-title" style="font-size: 14px;">\${item.name}</span>
                </div>
                <div class="cat-arrow">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"></path></svg>
                </div>
            </div>
        </div>
    \`).join('');
    
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
`;

js = js + subCatalogCode;
fs.writeFileSync(filePath, js, 'utf-8');
console.log('Appended sub-catalog logic to app.js');
