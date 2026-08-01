import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

sub_catalog_js = r"""
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
"""

if "window.openSubCatalog =" not in js:
    js += "\n" + sub_catalog_js

with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("JS sub-catalog logic added.")
