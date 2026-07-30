"""
Модуль API безопасной передачи автомобилей при продаже (Transfers Router).

Реализует генерацию одноразового PIN-кода текущим владельцем
и безопасную активацию покупателем с переносом всей истории обслуживания на сервере.
"""

import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, Car, CarTransferCode
from app.schemas import TransferCodeGenerate, TransferCodeClaim, TransferByPhone, CarResponse
from app.routers.auth import get_current_client

router = APIRouter(
    prefix="/api/v1/transfers",
    tags=["Безопасная Передача Авто (Car Transfers)"]
)


from datetime import datetime, timedelta

@router.post("/generate-code")
def generate_transfer_code(
    data: TransferCodeGenerate,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    (Поточний власник) Генерація 6-значного SMS PIN-коду для продажу авто (дійсний 15 хвилин).
    """
    car = db.query(Car).filter(Car.id == data.car_id, Car.client_id == current_client.id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автомобіль не знайдено у вашому гаражі або він вам не належить"
        )

    part1 = random.randint(100, 999)
    part2 = random.randint(100, 999)
    pin = f"{part1}-{part2}"

    expires_at = datetime.utcnow() + timedelta(minutes=15)

    transfer_record = CarTransferCode(
        car_id=car.id,
        from_client_id=current_client.id,
        pin_code=pin,
        expires_at=expires_at
    )

    db.add(transfer_record)
    db.commit()

    return {
        "message": "PIN-код успішно згенеровано та надіслано в SMS",
        "pin_code": pin,
        "car": f"{car.brand} {car.model} ({car.vin})",
        "expires_in": "15 хвилин",
        "expires_at": expires_at.isoformat(),
        "instruction": f"Вам надіслано SMS із 6-значним PIN-кодом [{pin}]. Код дійсний 15 хвилин. Передайте його покупцю для миттєвого переносу авто та всієї сервісної книжки."
    }


@router.post("/claim", response_model=CarResponse)
def claim_car_by_pin(
    data: TransferCodeClaim,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    (Покупець) Активація 6-значного PIN-коду та прийом авто в свій Гараж.
    """
    clean_pin = data.pin_code.strip()

    record = db.query(CarTransferCode).filter(
        CarTransferCode.pin_code == clean_pin,
        CarTransferCode.is_used == False
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недійсний або вже використаний PIN-код"
        )

    if record.expires_at and record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Термін дії PIN-коду вичерпано (код дійсний лише 15 хвилин). Продавець має згенерувати новий PIN."
        )

    # 2. Находим автомобиль
    car = db.query(Car).filter(Car.id == record.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")

    # 3. БЕЗОПАСНАЯ ПЕРЕДАЧА: Меням владельца авто в базе на текущего клиента
    car.client_id = current_client.id
    record.is_used = True

    db.commit()
    db.refresh(car)

    return car


@router.post("/by-phone", response_model=CarResponse)
def transfer_car_by_phone(
    data: TransferByPhone,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    (Текущий владелец) Прямая передача авто по номеру телефона покупателя.
    """
    car = db.query(Car).filter(Car.id == data.car_id, Car.client_id == current_client.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Автомобиль не найден в вашем гараже")

    target_phone = data.target_phone.strip()
    target_client = db.query(Client).filter(Client.phone == target_phone).first()

    if not target_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Покупатель с номером {target_phone} не найден. Убедитесь, что покупатель зарегистрировался в приложении."
        )

    # Передача авто
    car.client_id = target_client.id
    db.commit()
    db.refresh(car)

    return car
