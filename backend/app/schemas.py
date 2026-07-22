"""
Модуль схем даних (Pydantic Schemas).

Включає схеми повернень, чату та способів оплати.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import re


# --- СХЕМИ АВТОМОБІЛЯ ТА ПЕРЕДАЧІ ---

class CarBase(BaseModel):
    vin: str = Field(..., description="VIN-код автомобіля (17 символів)")
    brand: str = Field(..., min_length=1, max_length=50, description="Марка авто")
    model: str = Field(..., min_length=1, max_length=50, description="Модель авто")
    modification: Optional[str] = Field(None, description="Модифікація / кузов")
    release_date: Optional[str] = Field(None, description="Рік або дата випуску")
    engine_code: Optional[str] = Field(None, description="Код двигуна")
    drive_type: Optional[str] = Field(None, description="Привід (FWD, AWD, RWD)")
    transmission_type: Optional[str] = Field(None, description="Тип КПП (АКПП / МКПП)")
    transmission_code: Optional[str] = Field(None, description="Код КПП")
    notes: Optional[str] = Field(None, description="Замітки")
    status: Optional[str] = Field("Ідентифіковано", description="Статус ідентифікації")

    @field_validator("vin")
    @classmethod
    def validate_and_clean_vin(cls, v: str) -> str:
        clean_vin = v.strip().upper()
        if len(clean_vin) != 17:
            raise ValueError(f"VIN-код повинен містити ровно 17 символів (передано {len(clean_vin)})")
        return clean_vin


class CarCreate(CarBase):
    client_id: Optional[int] = None


class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    modification: Optional[str] = None
    release_date: Optional[str] = None
    engine_code: Optional[str] = None
    drive_type: Optional[str] = None
    transmission_type: Optional[str] = None
    transmission_code: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None



class CarResponse(CarBase):
    id: int
    client_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TransferCodeGenerate(BaseModel):
    car_id: int


class TransferCodeClaim(BaseModel):
    pin_code: str


class TransferByPhone(BaseModel):
    car_id: int
    target_phone: str



# --- СХЕМИ ЗАПРОСІВ ТА ЗМЕТ ---

class OrderRequestCreate(BaseModel):
    car_id: int
    client_message: str
    photo_url: Optional[str] = None


class ProposalAlternativeCreate(BaseModel):
    brand: str
    part_number: str
    price: float
    delivery_term: Optional[str] = "1-2 дні"


class ProposalItemCreate(BaseModel):
    category_name: str
    oem_number: Optional[str] = None
    alternatives: List[ProposalAlternativeCreate]


class ProposalCreate(BaseModel):
    request_id: int
    manager_comment: Optional[str] = None
    items: List[ProposalItemCreate]


class ProposalAlternativeResponse(ProposalAlternativeCreate):
    id: int
    is_selected: bool

    class Config:
        from_attributes = True


class ProposalItemResponse(BaseModel):
    id: int
    category_name: str
    oem_number: Optional[str] = None
    alternatives: List[ProposalAlternativeResponse] = []

    class Config:
        from_attributes = True


class ProposalResponse(BaseModel):
    id: int
    request_id: int
    car_id: int
    manager_comment: Optional[str] = None
    created_at: datetime
    valid_until: datetime
    items: List[ProposalItemResponse] = []

    class Config:
        from_attributes = True


class OrderRequestResponse(BaseModel):
    id: int
    client_id: int
    car_id: int
    client_message: str
    photo_url: Optional[str] = None
    status: str
    created_at: datetime
    car: Optional[CarResponse] = None
    proposal: Optional[ProposalResponse] = None

    class Config:
        from_attributes = True


# --- СХЕМИ ЗАМОВЛЕНЬ ТА ОПЛАТИ (ORDERS & PAYMENTS) ---

class OrderItemCreate(BaseModel):
    category_name: str
    oem_number: Optional[str] = None
    brand: str
    part_number: str
    price: float
    delivery_term: Optional[str] = "1-2 дні"


class OrderCreate(BaseModel):
    car_id: int
    proposal_id: Optional[int] = None
    payment_method: Optional[str] = Field("cash_on_delivery", description="cash_on_delivery / fop_prepayment / partial_prepayment")
    shipping_address: Optional[str] = None
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: Optional[str] = None
    assembly_photo_url: Optional[str] = None
    ttn_number: Optional[str] = None
    purchase_cost: Optional[float] = None


class OrderItemResponse(OrderItemCreate):
    id: int

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    client_id: int
    car_id: int
    proposal_id: Optional[int] = None
    status: str
    payment_method: str
    assembly_photo_url: Optional[str] = None
    ttn_number: Optional[str] = None
    ttn_tracking_url: Optional[str] = None
    total_price: float
    purchase_cost: Optional[float] = None
    shipping_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    car: Optional[CarResponse] = None
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


# --- СХЕМИ ПОВЕРНЕНЬ (RETURNS) ---

class OrderReturnCreate(BaseModel):
    order_id: int = Field(..., description="ID замовлення")
    reason: str = Field(..., min_length=5, description="Причина повернення")


class OrderReturnResponse(BaseModel):
    id: int
    order_id: int
    client_id: int
    reason: str
    return_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- СХЕМИ ЧАТУ (CHAT) ---

class ChatMessageCreate(BaseModel):
    request_id: int = Field(..., description="ID запиту")
    message: str = Field(..., min_length=1, description="Текст повідомлення")
    attachment_url: Optional[str] = Field(None, description="Ссылка на фото/техпаспорт")


class ChatMessageResponse(BaseModel):
    id: int
    request_id: int
    client_id: int
    sender_type: str
    message: str
    attachment_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- СХЕМИ КЛІЄНТА ---

class ClientRegister(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    middle_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    has_messenger: bool = True
    shipping_address: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean_phone = re.sub(r"[^\d+]", "", v.strip())
        if not clean_phone.startswith("+"):
            if clean_phone.startswith("380"):
                clean_phone = "+" + clean_phone
            elif clean_phone.startswith("0"):
                clean_phone = "+38" + clean_phone
        if len(clean_phone) < 10 or len(clean_phone) > 15:
            raise ValueError("Введіть коректний номер телефону (наприклад: +380931234567)")
        return clean_phone


class ClientLogin(BaseModel):
    phone: str


class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[str] = None
    has_messenger: Optional[bool] = None
    shipping_address: Optional[str] = None



class ClientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    has_messenger: bool
    shipping_address: Optional[str] = None
    auth_token: str
    completed_orders_count: int
    registered_at: datetime
    cars: List[CarResponse] = []

    class Config:
        from_attributes = True


class AuthTokenResponse(BaseModel):
    auth_token: str
    client: ClientResponse

