import io

with io.open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if 'let vinValue = clientVinInput.value.trim().toUpperCase();' in line:
        start_idx = i
        break

if start_idx != -1:
    for i in range(start_idx+1, len(lines)):
        if 'const fuelVal =' in lines[i]:
            end_idx = i
            break

if start_idx != -1 and end_idx != -1:
    new_lines = [
        '        let vinValue = clientVinInput.value.trim().toUpperCase();\n',
        '        if (vinValue) {\n',
        '            if (vinValue.length !== 17) {\n',
        '                showToast(\'❌ VIN-код має містити рівно 17 символів (якщо вказаний)!\', \'error\');\n',
        '                return;\n',
        '            } else if (/^\\d+$/.test(vinValue)) {\n',
        '                showToast(\'❌ VIN-код не може складатись лише з цифр! Введіть справжній VIN\', \'error\');\n',
        '                return;\n',
        '            }\n',
        '        }\n',
        '\n'
    ]
    lines[start_idx:end_idx] = new_lines
    with io.open('client_frontend/app.js', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Fixed VIN validation")
else:
    print("Could not find VIN validation block")
