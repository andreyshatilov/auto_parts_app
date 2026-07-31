import io

with io.open('backend/app/routers/clients.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    '# 1. Перевіряємо дублікати VIN',
    '''# 1. Генеруємо псевдо-VIN, якщо не вказано
    import uuid
    if not car_in.vin or car_in.vin.strip() == '':
        car_in.vin = f"NOVIN-{uuid.uuid4().hex[:10].upper()}"
        
    # 2. Перевіряємо дублікати VIN'''
)

with io.open('backend/app/routers/clients.py', 'w', encoding='utf-8') as f:
    f.write(code)
