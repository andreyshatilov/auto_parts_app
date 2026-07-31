import io

with io.open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "garageContainer.innerHTML = cars.map(car => {" in line:
        insert_idx = i - 1
        break

new_code = """
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
"""

lines.insert(insert_idx, new_code)

with io.open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Updated renderGarage add button")
