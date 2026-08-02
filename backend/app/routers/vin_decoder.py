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
    "WBS": {"brand": "BMW M", "country": "Німеччина", "region": "Європа"},
    "4US": {"brand": "BMW", "country": "США", "region": "Північна Америка"},
    "5UX": {"brand": "BMW", "country": "США", "region": "Північна Америка"},
    "WAU": {"brand": "Audi", "country": "Німеччина", "region": "Європа"},
    "WUA": {"brand": "Audi", "country": "Німеччина", "region": "Європа"},
    "WDB": {"brand": "Mercedes-Benz", "country": "Німеччина", "region": "Європа"},
    "WDC": {"brand": "Mercedes-Benz", "country": "Німеччина", "region": "Європа"},
    "WDD": {"brand": "Mercedes-Benz", "country": "Німеччина", "region": "Європа"},
    "W1K": {"brand": "Mercedes-Benz", "country": "Німеччина", "region": "Європа"},
    "W1N": {"brand": "Mercedes-Benz", "country": "Німеччина", "region": "Європа"},
    "4JG": {"brand": "Mercedes-Benz", "country": "США", "region": "Північна Америка"},
    "WVW": {"brand": "Volkswagen", "country": "Німеччина", "region": "Європа"},
    "WVG": {"brand": "Volkswagen", "country": "Німеччина", "region": "Європа"},
    "3VW": {"brand": "Volkswagen", "country": "Мексика", "region": "Північна Америка"},
    "3G1": {"brand": "Chevrolet", "country": "Мексика / США", "region": "Північна Америка"},
    "1G1": {"brand": "Chevrolet", "country": "США", "region": "Північна Америка"},
    "KL1": {"brand": "Chevrolet", "country": "Південна Корея", "region": "Азія"},
    "VF1": {"brand": "Renault", "country": "Франція", "region": "Європа"},
    "VF3": {"brand": "Peugeot", "country": "Франція", "region": "Європа"},
    "VF7": {"brand": "Citroen", "country": "Франція", "region": "Європа"},
    "JT1": {"brand": "Toyota", "country": "Японія", "region": "Азія"},
    "JTE": {"brand": "Toyota", "country": "Японія", "region": "Азія"},
    "JTD": {"brand": "Toyota", "country": "Японія", "region": "Азія"},
    "4T1": {"brand": "Toyota", "country": "США", "region": "Північна Америка"},
    "2T1": {"brand": "Toyota", "country": "Канада", "region": "Північна Америка"},
    "JM1": {"brand": "Mazda", "country": "Японія", "region": "Азія"},
    "JHM": {"brand": "Honda", "country": "Японія", "region": "Азія"},
    "SHH": {"brand": "Honda", "country": "Великобританія", "region": "Європа"},
    "1FA": {"brand": "Ford", "country": "США", "region": "Північна Америка"},
    "1FM": {"brand": "Ford", "country": "США", "region": "Північна Америка"},
    "WF0": {"brand": "Ford", "country": "Німеччина", "region": "Європа"},
    "TMB": {"brand": "Skoda", "country": "Чехія", "region": "Європа"},
    "ZFA": {"brand": "Fiat", "country": "Італія", "region": "Європа"},
    "KNA": {"brand": "Kia", "country": "Південна Корея", "region": "Азія"},
    "KNE": {"brand": "Kia", "country": "Південна Корея", "region": "Азія"},
    "KMH": {"brand": "Hyundai", "country": "Південна Корея", "region": "Азія"},
    "TMA": {"brand": "Hyundai", "country": "Чехія", "region": "Європа"},
    "SAL": {"brand": "Land Rover", "country": "Великобританія", "region": "Європа"},
    "SAJ": {"brand": "Jaguar", "country": "Великобританія", "region": "Європа"},
    "YV1": {"brand": "Volvo", "country": "Швеція", "region": "Європа"},
    "WP0": {"brand": "Porsche", "country": "Німеччина", "region": "Європа"},
    "WP1": {"brand": "Porsche", "country": "Німеччина", "region": "Європа"},
    "ZAR": {"brand": "Alfa Romeo", "country": "Італія", "region": "Європа"},
    "JN1": {"brand": "Nissan", "country": "Японія", "region": "Азія"},
    "VSS": {"brand": "SEAT", "country": "Іспанія", "region": "Європа"},
    "SUF": {"brand": "Fiat", "country": "Польща", "region": "Європа"},
    "SCC": {"brand": "Lotus", "country": "Великобританія", "region": "Європа"},
    "VNK": {"brand": "Toyota", "country": "Франція/Турція", "region": "Європа"},
}


def infer_generation(brand: Optional[str], model: Optional[str], year_str: Optional[str], vin: str = "") -> Optional[str]:
    """
    Інтелектуальне визначення точного покоління / кузова за маркою, моделлю, роком та VIN-кодом.
    (Наприклад: BMW 530i 2019 -> G30 / G31, Audi A4 2017 -> B9, VW Passat 2016 -> B8, Mercedes C300 -> W205)
    """
    vin_upper = (vin or '').upper().strip()
    prefix = vin_upper[:3]
    v_mid = vin_upper[3:9] if len(vin_upper) >= 9 else ''

    b_upper = (brand or '').upper().strip()
    m_upper = (model or '').upper().strip()

    # --- Спеціальне розпізнавання за європейським кодом кузова у VIN ---
    if 'AUDI' in b_upper or prefix in ['WAU', 'WUA']:
        if '8K' in v_mid: return 'B8 (8K)'
        if '8W' in v_mid: return 'B9 (8W)'
        if '8E' in v_mid: return 'B6 / B7 (8E)'
        if '4G' in v_mid: return 'C7 (4G)'
        if '4K' in v_mid: return 'C8 (4K)'
        if '4F' in v_mid: return 'C6 (4F)'
        if '8V' in v_mid: return '8V (3-тє пок.)'
        if '8Y' in v_mid: return '8Y (4-те пок.)'
        if '8P' in v_mid: return '8P (2-ге пок.)'
        if '8R' in v_mid: return '8R (1-ше пок.)'
        if 'FY' in v_mid: return 'FY (2-ге пок.)'
        if '4L' in v_mid: return '4L (1-ше пок.)'
        if '4M' in v_mid: return '4M (2-ге пок.)'

    if 'MERCEDES' in b_upper or prefix in ['WDB', 'WDC', 'WDD', 'W1K', 'W1N']:
        sub = vin_upper[3:7]
        if '206' in sub: return 'W206'
        if '205' in sub: return 'W205'
        if '204' in sub: return 'W204'
        if '203' in sub: return 'W203'
        if '214' in sub: return 'W214'
        if '213' in sub: return 'W213'
        if '212' in sub: return 'W212'
        if '211' in sub: return 'W211'
        if '223' in sub: return 'W223'
        if '222' in sub: return 'W222'
        if '221' in sub: return 'W221'
        if '167' in sub: return 'V167 / X167'
        if '166' in sub: return 'W166 (ML/GLE)'
        if '164' in sub: return 'W164 (ML)'

    if 'VOLKSWAGEN' in b_upper or 'VW' in b_upper or prefix in ['WVW', 'WVG', '3VW']:
        if '3C' in v_mid: return 'Passat B6 / B7'
        if '3G' in v_mid or 'CB' in v_mid: return 'Passat B8'
        if '5G' in v_mid or 'AU' in v_mid: return 'Golf 7 (MK7)'
        if 'CD' in v_mid: return 'Golf 8 (MK8)'
        if '1K' in v_mid: return 'Golf 5 / 6'
        if '5N' in v_mid: return 'Tiguan 1 (5N)'
        if 'AD' in v_mid or 'AX' in v_mid: return 'Tiguan 2 (AD1)'
        if '7P' in v_mid: return 'Touareg 2 (7P)'
        if 'CR' in v_mid: return 'Touareg 3 (CR7)'

    try:
        year = int(str(year_str).strip())
    except (ValueError, TypeError):
        year = None

    if not year:
        return None

    # --- BMW (За роком та моделлю) ---
    if 'BMW' in b_upper or prefix in ['WBA', 'WBY', 'WBS', '4US', '5UX']:
        # 1 Series
        if any(x in m_upper for x in ['1-SERIES', '1 SERIES', '116', '118', '120', '125', '130', '135', 'M135']) or m_upper == '1':
            if year >= 2019: return 'F40'
            elif year >= 2011: return 'F20 / F21'
            elif year >= 2004: return 'E81 / E82 / E87 / E88'

        # 2 Series
        if any(x in m_upper for x in ['2-SERIES', '2 SERIES', '218', '220', '228', '230', 'M235', 'M240', 'M2']) or m_upper == '2':
            if year >= 2021: return 'G42'
            elif year >= 2014: return 'F22 / F23 / F87'

        # 3 Series
        if any(x in m_upper for x in ['3-SERIES', '3 SERIES', '316', '318', '320', '328', '330', '335', '340', 'M3']) or m_upper == '3':
            if year >= 2019: return 'G20 / G21'
            elif year >= 2012: return 'F30 / F31 / F34'
            elif year >= 2005: return 'E90 / E91 / E92 / E93'
            elif year >= 1998: return 'E46'
            elif year >= 1990: return 'E36'

        # 4 Series
        if any(x in m_upper for x in ['4-SERIES', '4 SERIES', '420', '428', '430', '435', '440', 'M4']) or m_upper == '4':
            if year >= 2021: return 'G22 / G23 / G26'
            elif year >= 2014: return 'F32 / F33 / F36'

        # 5 Series
        if any(x in m_upper for x in ['5-SERIES', '5 SERIES', '520', '523', '525', '528', '530', '535', '540', '550', 'M5']) or m_upper == '5':
            if year >= 2024: return 'G60'
            elif year >= 2017: return 'G30 / G31'
            elif year >= 2010: return 'F10 / F11 / F07'
            elif year >= 2003: return 'E60 / E61'
            elif year >= 1995: return 'E39'

        # 6 Series
        if any(x in m_upper for x in ['6-SERIES', '6 SERIES', '630', '640', '650', 'M6']) or m_upper == '6':
            if year >= 2017: return 'G32 GT'
            elif year >= 2011: return 'F06 / F12 / F13'
            elif year >= 2003: return 'E63 / E64'

        # 7 Series
        if any(x in m_upper for x in ['7-SERIES', '7 SERIES', '730', '740', '750', '760', 'M7']) or m_upper == '7':
            if year >= 2023: return 'G70'
            elif year >= 2016: return 'G11 / G12'
            elif year >= 2009: return 'F01 / F02'
            elif year >= 2002: return 'E65 / E66'

        # X1
        if 'X1' in m_upper:
            if year >= 2022: return 'U11'
            elif year >= 2015: return 'F48'
            elif year >= 2009: return 'E84'

        # X2
        if 'X2' in m_upper:
            if year >= 2024: return 'U10'
            elif year >= 2017: return 'F39'

        # X3
        if 'X3' in m_upper:
            if year >= 2025: return 'G45'
            elif year >= 2018: return 'G01'
            elif year >= 2011: return 'F25'
            elif year >= 2004: return 'E83'

        # X4
        if 'X4' in m_upper:
            if year >= 2018: return 'G02'
            elif year >= 2014: return 'F26'

        # X5
        if 'X5' in m_upper:
            if year >= 2019: return 'G05'
            elif year >= 2014: return 'F15'
            elif year >= 2007: return 'E70'
            elif year >= 2000: return 'E53'

        # X6
        if 'X6' in m_upper:
            if year >= 2020: return 'G06'
            elif year >= 2015: return 'F16'
            elif year >= 2008: return 'E71'

        # X7
        if 'X7' in m_upper:
            if year >= 2019: return 'G07'

    # --- AUDI ---
    elif 'AUDI' in b_upper:
        if 'A3' in m_upper or 'S3' in m_upper or 'RS3' in m_upper:
            if year >= 2020: return '8Y (4-те пок.)'
            elif year >= 2013: return '8V (3-тє пок.)'
            elif year >= 2003: return '8P (2-ге пок.)'

        if 'A4' in m_upper or 'S4' in m_upper or 'RS4' in m_upper:
            if year >= 2024: return 'B10'
            elif year >= 2016: return 'B9 (8W)'
            elif year >= 2008: return 'B8 (8K)'
            elif year >= 2004: return 'B7 (8E)'
            elif year >= 2001: return 'B6 (8E)'

        if 'A5' in m_upper or 'S5' in m_upper or 'RS5' in m_upper:
            if year >= 2017: return 'F5 (2-ге пок.)'
            elif year >= 2007: return '8T (1-ше пок.)'

        if 'A6' in m_upper or 'S6' in m_upper or 'RS6' in m_upper:
            if year >= 2019: return 'C8 (4K)'
            elif year >= 2011: return 'C7 (4G)'
            elif year >= 2004: return 'C6 (4F)'
            elif year >= 1997: return 'C5 (4B)'

        if 'A7' in m_upper or 'S7' in m_upper or 'RS7' in m_upper:
            if year >= 2018: return '4K8 (2-ге пок.)'
            elif year >= 2010: return '4G8 (1-ше пок.)'

        if 'A8' in m_upper or 'S8' in m_upper:
            if year >= 2018: return 'D5 (4N)'
            elif year >= 2010: return 'D4 (4H)'
            elif year >= 2002: return 'D3 (4E)'

        if 'Q3' in m_upper or 'SQ3' in m_upper:
            if year >= 2018: return 'F3 (2-ге пок.)'
            elif year >= 2011: return '8U (1-ше пок.)'

        if 'Q5' in m_upper or 'SQ5' in m_upper:
            if year >= 2024: return '3-тє пок.'
            elif year >= 2017: return 'FY (2-ге пок.)'
            elif year >= 2008: return '8R (1-ше пок.)'

        if 'Q7' in m_upper or 'SQ7' in m_upper:
            if year >= 2015: return '4M (2-ге пок.)'
            elif year >= 2005: return '4L (1-ше пок.)'

        if 'Q8' in m_upper:
            if year >= 2018: return '4MN (1-ше пок.)'

    # --- MERCEDES-BENZ ---
    elif 'MERCEDES' in b_upper:
        if any(x in m_upper for x in ['C-CLASS', 'C180', 'C200', 'C220', 'C250', 'C300', 'C350', 'C43', 'C63']) or m_upper == 'C':
            if year >= 2021: return 'W206'
            elif year >= 2014: return 'W205'
            elif year >= 2007: return 'W204'
            elif year >= 2000: return 'W203'

        if any(x in m_upper for x in ['E-CLASS', 'E200', 'E220', 'E250', 'E300', 'E350', 'E400', 'E500', 'E63']) or m_upper == 'E':
            if year >= 2023: return 'W214'
            elif year >= 2016: return 'W213'
            elif year >= 2009: return 'W212'
            elif year >= 2002: return 'W211'

        if any(x in m_upper for x in ['S-CLASS', 'S350', 'S400', 'S500', 'S550', 'S600', 'S63']) or m_upper == 'S':
            if year >= 2021: return 'W223'
            elif year >= 2014: return 'W222'
            elif year >= 2006: return 'W221'
            elif year >= 1998: return 'W220'

        if 'CLA' in m_upper:
            if year >= 2019: return 'C118'
            elif year >= 2013: return 'C117'

        if 'CLS' in m_upper:
            if year >= 2018: return 'C257'
            elif year >= 2010: return 'C218'
            elif year >= 2004: return 'C219'

        if 'GLA' in m_upper:
            if year >= 2020: return 'H247'
            elif year >= 2013: return 'X156'

        if 'GLC' in m_upper:
            if year >= 2022: return 'X254'
            elif year >= 2015: return 'X253'

        if 'GLE' in m_upper or 'ML' in m_upper:
            if year >= 2019: return 'V167'
            elif year >= 2012: return 'W166 (ML/GLE)'
            elif year >= 2005: return 'W164 (ML)'

        if 'GLS' in m_upper or 'GL' in m_upper:
            if year >= 2019: return 'X167'
            elif year >= 2012: return 'X166'
            elif year >= 2006: return 'X164'

        if 'G-CLASS' in m_upper or 'G63' in m_upper or 'G500' in m_upper:
            if year >= 2018: return 'W463 FL'
            elif year >= 1990: return 'W463'

    # --- VOLKSWAGEN ---
    elif 'VOLKSWAGEN' in b_upper or 'VW' in b_upper:
        if 'PASSAT' in m_upper:
            if year >= 2024: return 'B9'
            elif year >= 2015: return 'B8'
            elif year >= 2011: return 'B7'
            elif year >= 2005: return 'B6'
            elif year >= 1996: return 'B5 / B5+'

        if 'GOLF' in m_upper:
            if year >= 2020: return 'MK8 (Golf 8)'
            elif year >= 2013: return 'MK7 (Golf 7)'
            elif year >= 2008: return 'MK6 (Golf 6)'
            elif year >= 2003: return 'MK5 (Golf 5)'
            elif year >= 1997: return 'MK4 (Golf 4)'

        if 'JETTA' in m_upper:
            if year >= 2018: return 'MK7'
            elif year >= 2010: return 'MK6'
            elif year >= 2005: return 'MK5'

        if 'TIGUAN' in m_upper:
            if year >= 2024: return 'Tiguan 3'
            elif year >= 2016: return 'Tiguan 2 (AD1)'
            elif year >= 2007: return 'Tiguan 1 (5N)'

        if 'TOUAREG' in m_upper:
            if year >= 2018: return 'CR7 (3-тє пок.)'
            elif year >= 2010: return '7P (2-ге пок.)'
            elif year >= 2002: return '7L (1-ше пок.)'

    # --- SKODA ---
    elif 'SKODA' in b_upper:
        if 'OCTAVIA' in m_upper:
            if year >= 2020: return 'A8 (MK4)'
            elif year >= 2013: return 'A7 (MK3)'
            elif year >= 2004: return 'A5 (MK2)'
            elif year >= 1996: return 'Tour (A4)'

        if 'SUPERB' in m_upper:
            if year >= 2024: return 'B9 (MK4)'
            elif year >= 2015: return 'B8 (MK3)'
            elif year >= 2008: return 'B6 (MK2)'
            elif year >= 2001: return 'MK1'

        if 'KODIAQ' in m_upper:
            if year >= 2024: return 'Kodiaq 2'
            elif year >= 2016: return 'Kodiaq 1'

    # --- TOYOTA ---
    elif 'TOYOTA' in b_upper:
        if 'CAMRY' in m_upper:
            if year >= 2024: return 'XV80 (9-те пок.)'
            elif year >= 2017: return 'XV70 (8-ме пок.)'
            elif year >= 2011: return 'XV50 (7-ме пок.)'
            elif year >= 2006: return 'XV40 (6-те пок.)'

        if 'COROLLA' in m_upper:
            if year >= 2018: return 'E210 (12-те пок.)'
            elif year >= 2013: return 'E170 (11-те пок.)'
            elif year >= 2006: return 'E140 / E150'

        if 'RAV4' in m_upper or 'RAV 4' in m_upper:
            if year >= 2019: return 'XA50 (5-те пок.)'
            elif year >= 2012: return 'XA40 (4-те пок.)'
            elif year >= 2005: return 'XA30 (3-тє пок.)'

        if 'LAND CRUISER' in m_upper or 'PRADO' in m_upper:
            if 'PRADO' in m_upper:
                if year >= 2023: return 'J250'
                elif year >= 2009: return 'J150'
                elif year >= 2002: return 'J120'
            else:
                if year >= 2021: return 'LC300'
                elif year >= 2007: return 'LC200'
                elif year >= 1998: return 'LC100'

    # --- HONDA ---
    elif 'HONDA' in b_upper:
        if 'CIVIC' in m_upper:
            if year >= 2021: return '11-те пок. (FE/FL)'
            elif year >= 2016: return '10-те пок. (FC/FK)'
            elif year >= 2011: return '9-те пок. (FB/FG)'
            elif year >= 2005: return '8-ме пок. (FD/FA)'

        if 'ACCORD' in m_upper:
            if year >= 2023: return '11-те пок. (CY)'
            elif year >= 2017: return '10-те пок. (CV)'
            elif year >= 2012: return '9-те пок. (CR)'
            elif year >= 2007: return '8-ме пок. (CU/CP)'

        if 'CR-V' in m_upper or 'CRV' in m_upper:
            if year >= 2022: return '6-те пок. (RS)'
            elif year >= 2016: return '5-те пок. (RW)'
            elif year >= 2011: return '4-те пок. (RM)'
            elif year >= 2006: return '3-тє пок. (RE)'

    # --- FORD ---
    elif 'FORD' in b_upper:
        if 'FOCUS' in m_upper:
            if year >= 2018: return 'MK4'
            elif year >= 2011: return 'MK3'
            elif year >= 2004: return 'MK2'
            elif year >= 1998: return 'MK1'

        if 'MONDEO' in m_upper or 'FUSION' in m_upper:
            if year >= 2013: return 'MK5 / Fusion US'
            elif year >= 2007: return 'MK4'
            elif year >= 2000: return 'MK3'

        if 'MUSTANG' in m_upper:
            if year >= 2024: return 'S650'
            elif year >= 2015: return 'S550'
            elif year >= 2005: return 'S197'

        if 'ESCAPE' in m_upper or 'KUGA' in m_upper:
            if year >= 2020: return '4-те пок. / Kuga 3'
            elif year >= 2013: return '3-тє пок. / Kuga 2'
            elif year >= 2008: return '2-ге пок.'

    # --- HYUNDAI & KIA ---
    elif 'HYUNDAI' in b_upper or 'KIA' in b_upper:
        if 'TUCSON' in m_upper:
            if year >= 2020: return 'NX4 (4-те пок.)'
            elif year >= 2015: return 'TL (3-тє пок.)'
            elif year >= 2009: return 'ix35 / 2-ге пок.'

        if 'SANTA FE' in m_upper:
            if year >= 2023: return 'MX5 (5-те пок.)'
            elif year >= 2018: return 'TM (4-те пок.)'
            elif year >= 2012: return 'DM (3-тє пок.)'

        if 'SPORTAGE' in m_upper:
            if year >= 2021: return 'NQ5 (5-те пок.)'
            elif year >= 2015: return 'QL (4-те пок.)'
            elif year >= 2010: return 'SL (3-тє пок.)'

        if 'OPTIMA' in m_upper or 'K5' in m_upper:
            if year >= 2019: return 'DL3 (K5 5-те пок.)'
            elif year >= 2015: return 'JF (4-те пок.)'
            elif year >= 2010: return 'TF (3-тє пок.)'

    return None


def _translate_body_class(body_raw: str) -> str:
    """Перетворення англійського BodyClass з NHTSA на українську назву типу кузова."""
    if not body_raw:
        return None
    b_lower = body_raw.lower()
    if 'sedan' in b_lower or 'saloon' in b_lower:
        return 'Седан'
    elif 'suv' in b_lower or 'utility' in b_lower:
        return 'Кросовер / Позашляховик'
    elif 'hatchback' in b_lower:
        return 'Хетчбек'
    elif 'wagon' in b_lower or 'estate' in b_lower:
        return 'Універсал'
    elif 'coupe' in b_lower:
        return 'Купе'
    elif 'convertible' in b_lower or 'cabrio' in b_lower:
        return 'Кабріолет'
    elif 'van' in b_lower or 'minivan' in b_lower:
        return 'Мінівен'
    elif 'pickup' in b_lower or 'truck' in b_lower:
        return 'Пікап'
    return body_raw


def _translate_fuel(fuel_raw: str) -> str:
    """Перетворення типу палива з NHTSA на українську."""
    if not fuel_raw:
        return None
    f_lower = fuel_raw.lower()
    if 'gasoline' in f_lower or 'petrol' in f_lower:
        return 'Бензин'
    elif 'diesel' in f_lower:
        return 'Дизель'
    elif 'electric' in f_lower:
        return 'Електро'
    elif 'hybrid' in f_lower:
        return 'Гібрид'
    elif 'flex' in f_lower or 'lpg' in f_lower or 'cng' in f_lower:
        return 'Газ / Бензин (ГБО)'
    return fuel_raw


def _translate_transmission(trans_raw: str, speeds_raw: str = None) -> str:
    """Перетворення типу трансмісії з NHTSA на українську."""
    if not trans_raw:
        return None
    t_lower = trans_raw.lower()
    speed_suffix = f" {speeds_raw}-ст." if speeds_raw and speeds_raw.strip() and speeds_raw.strip() != '0' else ''
    if 'auto' in t_lower:
        return f'АКПП{speed_suffix}'
    elif 'manual' in t_lower:
        return f'МКПП{speed_suffix}'
    elif 'cvt' in t_lower:
        return f'Варіатор (CVT){speed_suffix}'
    elif 'dct' in t_lower or 'dual' in t_lower:
        return f'Робот (DSG/DCT){speed_suffix}'
    return trans_raw


def _translate_drive_type(drive_raw: str) -> str:
    """Перетворення типу приводу з NHTSA на українську."""
    if not drive_raw:
        return None
    d_lower = drive_raw.lower()
    if 'awd' in d_lower or 'all' in d_lower or '4wd' in d_lower or '4x4' in d_lower:
        return 'Повний (AWD/4WD)'
    elif 'fwd' in d_lower or 'front' in d_lower:
        return 'Передній (FWD)'
    elif 'rwd' in d_lower or 'rear' in d_lower:
        return 'Задній (RWD)'
    return drive_raw


@router.get("/decode")
def decode_vin(vin: str = Query(..., min_length=3, max_length=17, description="VIN-код для декодування")):
    """
    Повний міжнародний декодер VIN.
    Автоматично розпізнає марку, модель, рік, серію/покоління, кузов,
    двигун, потужність, трансмісію, привід, завод збірки та країну за VIN-кодом.
    Використовує безкоштовний NHTSA vPIC API (США) з фолбеком на внутрішній WMI-словник.
    """
    clean_vin = vin.strip().upper()
    prefix = clean_vin[:3]

    decoded_result = {
        "vin": clean_vin,
        "brand": None,
        "model": None,
        "release_year": None,
        "series": None,          # Серія (напр. 5-Series, 3-Series)
        "generation": None,      # Покоління / Кузов (напр. G30 / G31, F30, B9, W205)
        "trim": None,            # Комплектація (xDrive, Quattro, AMG)
        "body_type": None,       # Тип кузова (Седан, Купе)
        "engine": None,          # Двигун (2.0L)
        "engine_cylinders": None, # Кількість циліндрів
        "horse_power": None,     # Потужність (к.с.)
        "fuel": None,            # Тип палива
        "transmission": None,    # Трансмісія
        "drive_type": None,      # Привід
        "plant_city": None,      # Місто заводу
        "plant_country": None,   # Країна заводу
        "country": None,
        "is_decoded": False
    }

    # Повний декод через безкоштовний NHTSA vPIC API (тільки для 17-символьних VIN)
    if len(clean_vin) == 17:
        try:
            url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{clean_vin}?format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    raw_data = json.loads(response.read().decode('utf-8'))
                    results = raw_data.get('Results', [{}])[0]

                    # --- Основні поля ---
                    make = (results.get('Make') or '').strip()
                    model = (results.get('Model') or '').strip()
                    year = (results.get('ModelYear') or '').strip()
                    series = (results.get('Series') or '').strip()
                    series2 = (results.get('Series2') or '').strip()
                    trim = (results.get('Trim') or '').strip()
                    body_raw = (results.get('BodyClass') or '').strip()
                    drive_raw = (results.get('DriveType') or '').strip()
                    disp = (results.get('DisplacementL') or '').strip()
                    fuel_raw = (results.get('FuelTypePrimary') or '').strip()
                    trans_raw = (results.get('TransmissionStyle') or '').strip()
                    trans_speeds = (results.get('TransmissionSpeeds') or '').strip()
                    cylinders = (results.get('EngineCylinders') or '').strip()
                    engine_model = (results.get('EngineModel') or '').strip()
                    engine_hp = (results.get('EngineHP') or '').strip()
                    plant_city = (results.get('PlantCity') or '').strip()
                    plant_country = (results.get('PlantCountry') or '').strip()

                    # --- Бренд ---
                    if make:
                        decoded_result['brand'] = make.title()
                        decoded_result['is_decoded'] = True

                    # --- Модель ---
                    if model:
                        decoded_result['model'] = model

                    # --- Рік ---
                    if year and year.isdigit():
                        decoded_result['release_year'] = str(year)

                    # --- Серія ---
                    full_series = series
                    if series2:
                        full_series = f"{series} / {series2}" if series else series2
                    if full_series:
                        decoded_result['series'] = full_series

                    # --- Комплектація ---
                    if trim:
                        decoded_result['trim'] = trim

                    # --- Тип кузова ---
                    if body_raw:
                        decoded_result['body_type'] = _translate_body_class(body_raw)

                    # --- Двигун ---
                    if disp and disp != "0":
                        try:
                            l_val = round(float(disp), 1)
                            engine_str = f"{l_val}L"
                            if cylinders and cylinders != '0':
                                engine_str += f" {cylinders}-цил."
                            if engine_model:
                                engine_str += f" ({engine_model})"
                            decoded_result['engine'] = engine_str
                        except:
                            decoded_result['engine'] = f"{disp}L"

                    # --- Кількість циліндрів ---
                    if cylinders and cylinders != '0':
                        decoded_result['engine_cylinders'] = cylinders

                    # --- Потужність ---
                    if engine_hp and engine_hp != '0':
                        try:
                            hp_val = round(float(engine_hp))
                            decoded_result['horse_power'] = f"{hp_val} к.с."
                        except:
                            decoded_result['horse_power'] = f"{engine_hp} к.с."

                    # --- Паливо ---
                    if fuel_raw:
                        decoded_result['fuel'] = _translate_fuel(fuel_raw)

                    # --- Трансмісія ---
                    if trans_raw:
                        decoded_result['transmission'] = _translate_transmission(trans_raw, trans_speeds)

                    # --- Привід ---
                    if drive_raw:
                        decoded_result['drive_type'] = _translate_drive_type(drive_raw)

                    # --- Завод збірки ---
                    if plant_city and plant_country:
                        decoded_result['plant_city'] = plant_city.title()
                        decoded_result['plant_country'] = plant_country.title()
                    elif plant_country:
                        decoded_result['plant_country'] = plant_country.title()
                    elif plant_city:
                        decoded_result['plant_city'] = plant_city.title()

        except Exception as e:
            print(f"NHTSA API error for VIN {clean_vin}: {e}", flush=True)

    # Fallback: локальне розпізнавання бренду за WMI якщо API не повернуло
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
                "2": "Канада", "3": "Мексика",
                "J": "Японія", "K": "Південна Корея",
                "L": "Китай", "M": "Індія/Таїланд",
                "S": "Великобританія", "T": "Чехія/Угорщина",
                "W": "Німеччина", "Z": "Італія",
                "V": "Франція / Іспанія", "Y": "Швеція/Фінляндія"
            }
            decoded_result['country'] = region_map.get(first_char, "Невідома країна")

    # Якщо країну не встановлено з WMI, але є з NHTSA
    if not decoded_result['country'] and decoded_result.get('plant_country'):
        decoded_result['country'] = decoded_result['plant_country']

    # --- Інтелектуальне визначення точного покоління / кузова ---
    inferred_gen = infer_generation(
        brand=decoded_result['brand'],
        model=decoded_result['model'],
        year_str=decoded_result['release_year'],
        vin=clean_vin
    )
    if inferred_gen:
        decoded_result['generation'] = inferred_gen

    return decoded_result
