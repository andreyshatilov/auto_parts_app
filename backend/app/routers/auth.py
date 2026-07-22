"""
Модуль API авторизации и регистрации клиентов (Auth Router).

Реализует вход, регистрацию и проверку токена доступа.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Client
from app.schemas import ClientRegister, ClientLogin, ClientResponse, AuthTokenResponse

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Авторизация и Профиль (Auth)"]
)


def get_current_client(
    x_auth_token: Optional[str] = Header(None, alias="X-Auth-Token"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Client:
    """
    Зависимость для защиты API маршрутов клиента.
    Проверяет переданный токен в заголовках `X-Auth-Token` или `Authorization: Bearer <token>`.
    """
    token = x_auth_token

    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "").strip()
        else:
            token = authorization.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Для доступа к этой функции необходимо войти или зарегистрироваться (Токен не передан)"
        )

    client = db.query(Client).filter(Client.auth_token == token).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен сессии. Пожалуйста, войдите снова."
        )

    return client


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
def register_client(data: ClientRegister, db: Session = Depends(get_db)):
    """
    Регистрация нового клиента в приложении.
    
    - Проверяет, что телефон еще не зарегистрирован.
    - Генерирует токен сессии и создает личный кабинет.
    """
    # 1. Проверяем телефон на уникальность
    existing = db.query(Client).filter(Client.phone == data.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь с номером {data.phone} уже зарегистрирован! Нажмите 'Войти' для доступа к аккаунту."
        )

    # 2. Генерируем уникальный сессионный токен
    token = f"token_{uuid.uuid4().hex}"

    # 3. Создаем запись клиента
    new_client = Client(
        first_name=data.first_name,
        last_name=data.last_name,
        middle_name=data.middle_name,
        phone=data.phone,
        email=data.email,
        has_messenger=data.has_messenger,
        shipping_address=data.shipping_address,
        auth_token=token
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return {
        "auth_token": token,
        "client": new_client
    }


@router.post("/login", response_model=AuthTokenResponse)
def login_client(data: ClientLogin, db: Session = Depends(get_db)):
    """
    Вход в личный кабинет по номеру телефона.
    
    Восстанавливает весь гараж и историю заказов зарегистрированного клиента.
    """
    # Очистка формата телефона перед поиском
    phone_query = data.phone.strip()

    client = db.query(Client).filter(Client.phone == phone_query).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с номером {phone_query} не найден. Проверьте номер или зарегистрируйтесь."
        )

    return {
        "auth_token": client.auth_token,
        "client": client
    }


@router.get("/me", response_model=ClientResponse)
def get_my_profile(current_client: Client = Depends(get_current_client)):
    """
    Получение профиля вошедшего клиента по его токену.
    Возвращает личные данные и весь его "Гараж" автомобилей.
    """
    return current_client
