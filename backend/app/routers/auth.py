import uuid
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional
from passlib.context import CryptContext

from app.database import get_db
from app.models import Client, OTPCode
from app.schemas import ClientCreate, LoginRequest, ClientResponse, AuthTokenResponse, VerifyOTP, ForgotPassword, ResetPassword

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Авторизація та Клієнти (Auth)"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    try:
        return pwd_context.hash(password)
    except Exception:
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        import bcrypt
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_otp():
    return str(random.randint(100000, 999999))

def get_current_client_optional(
    x_auth_token: Optional[str] = Header(None, alias="X-Auth-Token"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[Client]:
    token = x_auth_token

    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "").strip()
        else:
            token = authorization.strip()

    if not token:
        return None

    client = db.query(Client).filter(Client.auth_token == token).first()
    return client

def get_current_client(
    x_auth_token: Optional[str] = Header(None, alias="X-Auth-Token"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Client:
    token = x_auth_token

    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "").strip()
        else:
            token = authorization.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не передано токен авторизації"
        )

    client = db.query(Client).filter(Client.auth_token == token).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний або прострочений токен"
        )

    return client


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_client(data: ClientCreate, db: Session = Depends(get_db)):
    """Реєстрація нового клієнта. Створює неактивний акаунт і генерує OTP."""
    try:
        existing_client = db.query(Client).filter(Client.phone == data.phone).first()
        
        if existing_client:
            # Якщо клієнт вже має пароль, значить це повноцінний існуючий акаунт
            if existing_client.hashed_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Клієнт з таким номером телефону вже існує!"
                )
            else:
                # Це "старий" клієнт (до введення паролів). Дозволяємо йому "зареєструватися" (оновити дані)
                if data.email:
                    existing_email = db.query(Client).filter(Client.email == data.email).first()
                    if existing_email and existing_email.id != existing_client.id:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Клієнт з таким Email вже існує!"
                        )
                
                existing_client.first_name = data.first_name
                existing_client.last_name = data.last_name
                existing_client.email = data.email
                existing_client.has_messenger = data.has_messenger
                existing_client.hashed_password = get_password_hash(data.password)
                existing_client.is_verified = False
                existing_client.auth_token = f"token_{uuid.uuid4().hex}"
                
                db.commit()
                db.refresh(existing_client)
                target_client = existing_client
        else:
            if data.email:
                existing_email = db.query(Client).filter(Client.email == data.email).first()
                if existing_email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Клієнт з таким Email вже існує!"
                    )

            token = f"token_{uuid.uuid4().hex}"
            
            new_client = Client(
                first_name=data.first_name,
                last_name=data.last_name,
                phone=data.phone,
                email=data.email,
                has_messenger=data.has_messenger,
                hashed_password=get_password_hash(data.password),
                is_verified=False,
                auth_token=token
            )
            db.add(new_client)
            db.commit()
            db.refresh(new_client)
            target_client = new_client

        # Генеруємо OTP
        if target_client.email:
            otp_val = generate_otp()
            otp_entry = OTPCode(
                email=target_client.email,
                code=otp_val,
                expires_at=datetime.utcnow() + timedelta(minutes=15)
            )
            db.add(otp_entry)
            db.commit()
            
            print(f"========== OTP CODE FOR {target_client.email} ==========", flush=True)
            print(f"CODE: {otp_val}", flush=True)
            print(f"=================================================", flush=True)

        return {"message": "OTP відправлено на email. Акаунт потребує верифікації."}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Помилка створення акаунта: {str(e)}"
        )


@router.post("/verify", response_model=AuthTokenResponse)
def verify_client_otp(data: VerifyOTP, db: Session = Depends(get_db)):
    """Перевірка OTP-коду та активація акаунта."""
    client = db.query(Client).filter(Client.email == data.email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клієнта з таким email не знайдено.")
        
    otp = db.query(OTPCode).filter(OTPCode.email == data.email).order_by(OTPCode.id.desc()).first()
    if not otp or otp.code != data.code:
        raise HTTPException(status_code=400, detail="Невірний код підтвердження.")
        
    if otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Код підтвердження прострочений.")
        
    client.is_verified = True
    db.commit()
    
    return {
        "auth_token": client.auth_token,
        "client": client
    }


@router.post("/login", response_model=AuthTokenResponse)
def login_client(data: LoginRequest, db: Session = Depends(get_db)):
    """Вхід за email/телефоном та паролем."""
    client = db.query(Client).filter(
        (Client.email == data.phone_or_email) | (Client.phone == data.phone_or_email)
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Користувача не знайдено.")
        
    if not client.is_verified:
        raise HTTPException(status_code=403, detail="Акаунт не підтверджено. Будь ласка, верифікуйте email.")
        
    if not client.hashed_password or not verify_password(data.password, client.hashed_password):
        raise HTTPException(status_code=401, detail="Невірний пароль.")

    return {
        "auth_token": client.auth_token,
        "client": client
    }


@router.post("/forgot-password")
def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    """Запит на скидання пароля."""
    client = db.query(Client).filter(Client.email == data.email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Акаунт з таким email не знайдено.")
        
    otp_val = generate_otp()
    otp_entry = OTPCode(
        email=data.email,
        code=otp_val,
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    db.add(otp_entry)
    db.commit()
    
    print(f"========== RESET PASSWORD OTP FOR {data.email} ==========", flush=True)
    print(f"CODE: {otp_val}", flush=True)
    print(f"=================================================", flush=True)
    
    return {"message": "Код для відновлення відправлено на email."}


@router.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    """Зміна пароля."""
    otp = db.query(OTPCode).filter(OTPCode.email == data.email).order_by(OTPCode.id.desc()).first()
    if not otp or otp.code != data.code:
        raise HTTPException(status_code=400, detail="Невірний код підтвердження.")
        
    if otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Код підтвердження прострочений.")
        
    client = db.query(Client).filter(Client.email == data.email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клієнта не знайдено.")
        
    client.hashed_password = get_password_hash(data.new_password)
    db.commit()
    
    return {"message": "Пароль успішно змінено!"}


@router.get("/me", response_model=ClientResponse)
def get_my_profile(current_client: Client = Depends(get_current_client)):
    return current_client
