"""
Модуль моделей базы данных (SQLAlchemy Models).

Описывает структуру таблиц:
1. `clients` — зарегистрированные клиенты.
2. `cars` — автомобили в личных гаражах клиентов.
3. `order_requests` — текстовые запросы на подбор запчастей.
4. `proposals`, `proposal_items`, `proposal_alternatives` — сметы эксперта.
5. `car_transfer_codes` — PIN-коды передачи авто при продаже.
6. `orders`, `order_items` — оформленные заказы с фото сборки и ТТН Новой Почты.
7. `order_returns` — заявки на возврат товара.
8. `chat_messages` — внутренний чат с экспертом.
9. `cross_references` — база знаний кросс-номеров (OE -> аналоги и цены) без ШИ.
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), nullable=True)
    has_messenger = Column(Boolean, default=True, nullable=False)
    shipping_address = Column(Text, nullable=True)
    auth_token = Column(String(64), unique=True, index=True, nullable=False)
    completed_orders_count = Column(Integer, default=0, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    cars = relationship("Car", back_populates="owner", cascade="all, delete-orphan")
    requests = relationship("OrderRequest", back_populates="client")
    orders = relationship("Order", back_populates="client")
    returns = relationship("OrderReturn", back_populates="client")
    chat_messages = relationship("ChatMessage", back_populates="client")


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)
    vin = Column(String(17), unique=True, index=True, nullable=False)
    brand = Column(String(50), nullable=False, index=True)
    model = Column(String(50), nullable=False)
    modification = Column(String(100), nullable=True)
    release_date = Column(String(20), nullable=True)
    engine_code = Column(String(50), nullable=True, index=True)
    drive_type = Column(String(30), nullable=True)
    transmission_type = Column(String(30), nullable=True)
    transmission_code = Column(String(50), nullable=True)
    notes = Column(String(255), nullable=True)
    status = Column(String(50), default="Ідентифіковано", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("Client", back_populates="cars")
    requests = relationship("OrderRequest", back_populates="car")
    proposals = relationship("Proposal", back_populates="car")
    orders = relationship("Order", back_populates="car")


class OrderRequest(Base):
    __tablename__ = "order_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, index=True)
    client_message = Column(Text, nullable=False)
    photo_url = Column(String(255), nullable=True)
    status = Column(String(30), default="sent", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    client = relationship("Client", back_populates="requests")
    car = relationship("Car", back_populates="requests")
    proposal = relationship("Proposal", back_populates="request", uselist=False)
    chat_messages = relationship("ChatMessage", back_populates="request", cascade="all, delete-orphan")


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("order_requests.id"), nullable=False, unique=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    manager_comment = Column(Text, nullable=True)
    valid_until = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    request = relationship("OrderRequest", back_populates="proposal")
    car = relationship("Car", back_populates="proposals")
    items = relationship("ProposalItem", back_populates="proposal", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="proposal")


class ProposalItem(Base):
    __tablename__ = "proposal_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False, index=True)
    category_name = Column(String(100), nullable=False)
    oem_number = Column(String(50), nullable=True)

    proposal = relationship("Proposal", back_populates="items")
    alternatives = relationship("ProposalAlternative", back_populates="item", cascade="all, delete-orphan")


class ProposalAlternative(Base):
    __tablename__ = "proposal_alternatives"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("proposal_items.id"), nullable=False, index=True)
    brand = Column(String(50), nullable=False)
    part_number = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    delivery_term = Column(String(50), default="1-2 дні")
    is_selected = Column(Boolean, default=False)

    item = relationship("ProposalItem", back_populates="alternatives")


class CarTransferCode(Base):
    __tablename__ = "car_transfer_codes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, index=True)
    from_client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    pin_code = Column(String(10), unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=48), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=True)

    status = Column(String(30), default="sent_to_preparation", nullable=False)
    assembly_photo_url = Column(String(255), nullable=True)
    ttn_number = Column(String(50), nullable=True)
    ttn_tracking_url = Column(String(255), nullable=True)
    payment_method = Column(String(50), default="cash_on_delivery", nullable=False)

    total_price = Column(Numeric(10, 2), nullable=False)
    purchase_cost = Column(Numeric(10, 2), nullable=True)

    shipping_address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    client = relationship("Client", back_populates="orders")
    car = relationship("Car", back_populates="orders")
    proposal = relationship("Proposal", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    returns = relationship("OrderReturn", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    category_name = Column(String(100), nullable=False)
    oem_number = Column(String(50), nullable=True)
    brand = Column(String(50), nullable=False)
    part_number = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    delivery_term = Column(String(50), default="1-2 дні")

    order = relationship("Order", back_populates="items")


class OrderReturn(Base):
    __tablename__ = "order_returns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    return_type = Column(String(30), nullable=False)
    status = Column(String(30), default="requested", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="returns")
    client = relationship("Client", back_populates="returns")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("order_requests.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    sender_type = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    attachment_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    request = relationship("OrderRequest", back_populates="chat_messages")
    client = relationship("Client", back_populates="chat_messages")


class CrossReference(Base):
    """База знань крос-номерів (OE -> бренди, артикули, ціни) без ШІ"""
    __tablename__ = "cross_references"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    oem_number_clean = Column(String(50), index=True, nullable=False) # Тільки букви та цифри без пробілів
    oem_number_raw = Column(String(50), nullable=False)
    category_name = Column(String(100), nullable=True)
    brand = Column(String(50), nullable=False)
    part_number = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    times_used = Column(Integer, default=1, nullable=False)
    source_file = Column(String(100), nullable=True)
