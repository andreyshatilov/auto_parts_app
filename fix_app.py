import io
import sys

try:
    with io.open('client_frontend/app.js', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start_idx = -1
    for i, line in enumerate(lines):
        if "document.getElementById('detailCarBrandEmblem').innerHTML = getBrandEmblem(car.brand);" in line:
            start_idx = i + 2
            break

    if start_idx == -1:
        print("Could not find start string")
        sys.exit(1)

    end_idx = start_idx + 12

    new_lines = [
        "    const genDisplay = car.generation ? car.generation : (car.body_type ? car.body_type : '-');\n",
        "    document.getElementById('detailCarGeneration').textContent = genDisplay;\n",
        "    document.getElementById('detailCarYear').textContent = car.release_date ? `${car.release_date} р.в.` : '-';\n",
        "    \n",
        "    const engineDisplay = car.engine_code || '-';\n",
        "    const hpDisplay = car.horse_power || '-';\n",
        "    document.getElementById('detailCarEngine').textContent = `${engineDisplay} | ${hpDisplay}`;\n",
        "    \n",
        "    document.getElementById('detailCarFuel').textContent = `${car.fuel_type || '-'} | ${car.drive_type || '-'}`;\n",
        "    document.getElementById('detailCarTrans').textContent = `${car.transmission_type || '-'} ${car.transmission_code ? `(${car.transmission_code})` : ''}`;\n",
        "    document.getElementById('detailCarColor').textContent = car.color_code || '-';\n",
        "    document.getElementById('detailCarPlant').textContent = car.assembly_plant || '-';\n"
    ]

    lines[start_idx:end_idx] = new_lines

    with io.open('client_frontend/app.js', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Success")
except Exception as e:
    print(e)
