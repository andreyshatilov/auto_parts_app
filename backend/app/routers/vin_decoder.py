import urllib.request
import json
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

router = APIRouter(
    prefix="/api/v1/vin",
    tags=["Автономний Декодер VIN (VIN Decoder Engine)"]
)

# Словник WMI кодів світових автовиробників (fallback)
WMI_MAP = {
    "WBA": {"brand": "BMW", "country": "Німеччина", "region": "Європа"},
    "WBY": {"brand": "BMW", "country": "Німеччина", "region": "Європа"},
    "4US": {"brand": "BMW", "country": "США", "region": "Північна Америка"},
    "WAU": {"brand": "Audi", "country": "Німеччина", "region": "Європа"},
    "WDB": {"brand": "Mercedes-Benz", "country": "Німеччина", "region": "Європа"},
    "W1K": {"brand": "Mercedes-Benz", "country": "Німеччина", "region": "Європа"},
    "4JG": {"brand": "Mercedes-Benz", "country": "США", "region": "Північна Америка"},
    "WVW": {"brand": "Volkswagen", "country": "Німеччина", "region": "Європа"},
    "3VW": {"brand": "Volkswagen", "country": "Мексика", "region": "Північна Америка"},
    "3G1": {"brand": "Chevrolet", "country": "Мексика / США", "region": "Північна Америка"},
    "1G1": {"brand": "Chevrolet", "country": "США", "region": "Північна Америка"},
    "KL1": {"brand": "Chevrolet", "country": "Південна Корея", "region": "Азія"},
    "VF1": {"brand": "Renault", "country": "Франція", "region": "Європа"},
    "VF3": {"brand": "Peugeot", "country": "Франція", "region": "Європа"},
    "JT1": {"brand": "Toyota", "country": "Японія", "region": "Азія"},
    "JTE": {"brand": "Toyota", "country": "Японія", "region": "Азія"},
    "4T1": {"brand": "Toyota", "country": "США", "region": "Північна Америка"},
    "JM1": {"brand": "Mazda", "country": "Японія", "region": "Азія"},
    "JHM": {"brand": "Honda", "country": "Японія", "region": "Азія"},
    "1FA": {"brand": "Ford", "country": "США", "region": "Північна Америка"},
    "WF0": {"brand": "Ford", "country": "Німеччина", "region": "Європа"},
    "TMB": {"brand": "Skoda", "country": "Чехія", "region": "Європа"},
    "ZFA": {"brand": "Fiat", "country": "Італія", "region": "Європа"},
    "KNA": {"brand": "Kia", "country": "Південна Корея", "region": "Азія"},
    "KMH": {"brand": "Hyundai", "country": "Південна Корея", "region": "Азія"},
    "SAL": {"brand": "Land Rover", "country": "Великобританія", "region": "Європа"},
    "YV1": {"brand": "Volvo", "country": "Швеція", "region": "Європа"},
    "WP0": {"brand": "Porsche", "country": "Німеччина", "region": "Європа"}
}


@router.get("/decode")
def decode_vin(vin: str = Query(..., min_length=3, max_length=17, description="VIN-код для декодування")):
    """
    (Безкоштовний міжнародний декодер) Автоматично розпізнає марку, модель, рік, об'єм двигуна та тип палива за VIN-кодом.
    """
    clean_vin = vin.strip().upper()
    prefix = clean_vin[:3]

    decoded_result = {
        "vin": clean_vin,
        "brand": None,
        "model": None,
        "release_year": None,
        "body_type": None,
        "engine": None,
        "fuel": None,
        "transmission": None,
        "country": None,
        "is_decoded": False
    }

    # Спроба отримати детальну інформацію через безкоштовний глобальний NHTSA API (якщо VIN 17 символів)
    if len(clean_vin) == 17:
        try:
            url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{clean_vin}?format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3.5) as response:
                if response.status == 200:
                    raw_data = json.loads(response.read().decode('utf-8'))
                    results = raw_data.get('Results', [{}])[0]

                    make = results.get('Make')
                    model = results.get('Model')
                    year = results.get('ModelYear')
                    disp = results.get('DisplacementL')
                    fuel_raw = results.get('FuelTypePrimary', '')
                    trans_raw = results.get('TransmissionStyle', '')
                    body_raw = results.get('BodyClass', '')

                    if make and make.strip():
                        decoded_result['brand'] = make.strip().title()
                        decoded_result['is_decoded'] = True

                    if model and model.strip():
                        decoded_result['model'] = model.strip()

                    if year and year.isdigit():
                        decoded_result['release_year'] = str(year)

                    if disp and disp.strip() and disp.strip() != "0":
                        try:
                            l_val = round(float(disp), 1)
                            decoded_result['engine'] = f"{l_val}L"
                        except:
                            decoded_result['engine'] = f"{disp}L"

                    if body_raw:
                        b_lower = body_raw.lower()
                        if 'sedan' in b_lower:
                            decoded_result['body_type'] = 'Седан'
                        elif 'suv' in b_lower or 'utility' in b_lower:
                            decoded_result['body_type'] = 'Кросовер / Позашляховик'
                        elif 'hatchback' in b_lower:
                            decoded_result['body_type'] = 'Хетчбек'
                        elif 'wagon' in b_lower or 'estate' in b_lower:
                            decoded_result['body_type'] = 'Універсал'
                        elif 'coupe' in b_lower:
                            decoded_result['body_type'] = 'Купе'
                        elif 'convertible' in b_lower or 'cabrio' in b_lower:
                            decoded_result['body_type'] = 'Кабріолет'
                        elif 'van' in b_lower or 'minivan' in b_lower:
                            decoded_result['body_type'] = 'Мінівен'
                        elif 'pickup' in b_lower or 'truck' in b_lower:
                            decoded_result['body_type'] = 'Пікап'

                    if fuel_raw:
                        f_lower = fuel_raw.lower()
                        if 'gasoline' in f_lower or 'petrol' in f_lower:
                            decoded_result['fuel'] = 'Бензин'
                        elif 'diesel' in f_lower:
                            decoded_result['fuel'] = 'Дизель'
                        elif 'electric' in f_lower:
                            decoded_result['fuel'] = 'Електро'
                        elif 'hybrid' in f_lower:
                            decoded_result['fuel'] = 'Гібрид'
                        elif 'flex' in f_lower or 'lpg' in f_lower or 'cng' in f_lower:
                            decoded_result['fuel'] = 'Газ / Бензин (ГБО)'

                    if trans_raw:
                        t_lower = trans_raw.lower()
                        if 'auto' in t_lower:
                            decoded_result['transmission'] = 'АКПП'
                        elif 'manual' in t_lower:
                            decoded_result['transmission'] = 'МКПП'

        except Exception as e:
            pass

    # Fallback локальне розпізнавання бренду за WMI якщо API не повернуло марок
    if not decoded_result['brand']:
        info = WMI_MAP.get(prefix)
        if info:
            decoded_result['brand'] = info['brand']
            decoded_result['country'] = info['country']
            decoded_result['is_decoded'] = True
        else:
            first_char = clean_vin[0]
            region_map = {
                "1": "США", "4": "США", "5": "США",
                "J": "Японія", "K": "Південна Корея",
                "W": "Німеччина", "Z": "Італія", "V": "Франція / Іспанія"
            }
            decoded_result['country'] = region_map.get(first_char, "Невідома країна")

    return decoded_result

