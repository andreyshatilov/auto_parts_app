"""
Модуль подключения к базе данных (Database Setup).

Мы используем SQLAlchemy — профессиональную библиотеку в Python для работы с БД.
По умолчанию данные сохраняются в локальный файл `auto_parts.db` (SQLite).
В будущем, при переезде на PostgreSQL, достаточно будет просто изменить строку DATABASE_URL!
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # SQLAlchemy requires 'postgresql://' instead of legacy 'postgres://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "..", "auto_parts.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

# Фабрика сессий для взаимодействия с базами данных в каждом сетевом запросе
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех наших таблиц (Моделей)
Base = declarative_base()


def get_db():
    """
    Вспомогательная функция (Dependency injection для FastAPI).
    Открывает сессию связи с БД перед выполнением запроса
    и ГАРАНТИРОВАННО закрывает её после ответа клиенту.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
