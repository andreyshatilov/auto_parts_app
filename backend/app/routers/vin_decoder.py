"""
Модуль API-маршрутів для автономного декодування VIN-коду (VIN Decoder Router).

Визначає марку, країну походження та кузов авто за WMI префіксом (перші 3 символи VIN).
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException

router = APIRouter(
    prefix="/api/v1/vin",
    tags=["Автономний Декодер VIN (VIN Decoder Engine)"]
)

# Словник WMI кодів світових автовиробників
WMI_MAP = {
    "WBA": {"brand": "BMW", "country": "Німеччина", "region": "Європа"},
    "WBY": {"brand": "BMW i Series", "country": "Німеччина", "region": "Європа"},
    "4US": {"brand": "BMW (USA)", "country": "США", "region": "Північна Америка"},
    "WAU": {"brand": "Audi", "country": "Німеччина", "region": "Європа"},
    "WDB": {"brand": "Mercedes-Benz", "country": "Німеччина", "region": "Європа"},
    "W1K": {"brand": "Mercedes-Benz", "country": "Німеччина", "region": "Європа"},
    "4JG": {"brand": "Mercedes-Benz (USA)", "country": "США", "region": "Північна Америка"},
    "WVW": {"brand": "Volkswagen", "country": "Німеччина", "region": "Європа"},
    "3VW": {"brand": "Volkswagen (Mexico)", "country": "Мексика", "region": "Північна Америка"},
    "3G1": {"brand": "Chevrolet", "country": "Мексика / США", "region": "Північна Америка"},
    "1G1": {"brand": "Chevrolet", "country": "США", "region": "Північна Америка"},
    "KL1": {"brand": "Chevrolet (Daewoo)", "country": "Південна Корея", "region": "Азія"},
    "VF1": {"brand": "Renault", "country": "Франція", "region": "Європа"},
    "VF3": {"brand": "Peugeot", "country": "Франція", "region": "Європа"},
    "JT1": {"brand": "Toyota", "country": "Японія", "region": "Азія"},
    "JTE": {"brand": "Toyota SUV", "country": "Японія", "region": "Азія"},
    "4T1": {"brand": "Toyota (USA)", "country": "США", "region": "Північна Америка"},
    "JM1": {"brand": "Mazda", "country": "Японія", "region": "Азія"},
    "JHM": {"brand": "Honda", "country": "Японія", "region": "Азія"}
}


@router.get("/decode")
def decode_vin(vin: str = Query(..., min_length=3, max_length=17, description="VIN-код для декодування")):
    """
    (Безкоштовний автономний декодер) Автоматично визначає марку та країну за першими 3 символами VIN.
    """
    clean_vin = vin.strip().upper()
    prefix = clean_vin[:3]

    info = WMI_MAP.get(prefix)
    if not info:
        # Fallback розпізнавання за 1 символом (1/4/5 = США, J = Японія, K = Корея, W = Німеччина)
        first_char = clean_vin[0]
        region_map = {
            "1": "США", "4": "США", "5": "США",
            "J": "Японія", "K": "Південна Корея",
            "W": "Німеччина", "Z": "Італія", "V": "Франція / Іспанія"
        }
        country_est = region_map.get(first_char, "Невідома країна")
        return {
            "vin": clean_vin,
            "brand": "Невідома марка",
            "country": country_est,
            "is_decoded": False
        }

    return {
        "vin": clean_vin,
        "brand": info["brand"],
        "country": info["country"],
        "region": info["region"],
        "is_decoded": True
    }
