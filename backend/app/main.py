"""
Головний модуль веб-сервера FastAPI (Application Entry Point).

Підключає всі 14 роутерів системи.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.database import engine, Base
from app.routers import cars, auth, clients, requests, proposals, transfers, orders, returns, chat, payments, crosses, analytics, novaposhta, exports, vin_decoder, invoices

try:
    Base.metadata.create_all(bind=engine)
    
    # Auto-migration: ensure new columns exist in cars table in Neon PostgreSQL / SQLite
    from sqlalchemy import text
    with engine.connect() as conn:
        cols = [
            ("generation", "VARCHAR(50)"),
            ("body_type", "VARCHAR(50)"),
            ("fuel_type", "VARCHAR(50)"),
            ("horse_power", "VARCHAR(50)"),
            ("color_code", "VARCHAR(50)"),
            ("assembly_plant", "VARCHAR(100)"),
            ("mileage", "INTEGER DEFAULT 100000"),
            ("custom_photo_url", "TEXT")
        ]
        for c_name, c_type in cols:
            try:
                conn.execute(text(f"ALTER TABLE cars ADD COLUMN {c_name} {c_type};"))
                conn.commit()
            except Exception:
                conn.rollback()

        # Remove legacy numeric fake test VINs and test data entirely
        try:
            conn.execute(text("DELETE FROM cars WHERE vin = '23542435345643564';"))
            conn.commit()
        except Exception as e:
            print(f"Error purging test cars: {e}")
except Exception as err:
    print(f"⚠️ Database initialization notice: {err}")

app = FastAPI(
    title="Міністерство Запчастин - Повна Система Підбору та Замовлень Автозапчастин (Enterprise Production)",
    description="Повний комерційний бекенд з друком Товарних чеків, Сервісного паспорта авто, ТТН Нової Пошти, P&L аналітикою та бекапами.",
    version="2.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(cars.router)
app.include_router(transfers.router)
app.include_router(requests.router)
app.include_router(proposals.router)
app.include_router(orders.router)
app.include_router(returns.router)
app.include_router(chat.router)
app.include_router(payments.router)
app.include_router(crosses.router)
app.include_router(analytics.router)
app.include_router(novaposhta.router)
app.include_router(exports.router)
app.include_router(vin_decoder.router)
app.include_router(invoices.router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_frontend_dir(dir_name):
    p1 = os.path.abspath(os.path.join(BASE_DIR, "..", dir_name))
    if os.path.exists(p1):
        return p1
    p2 = os.path.abspath(os.path.join(BASE_DIR, "..", "..", dir_name))
    if os.path.exists(p2):
        return p2
    return p1

ADMIN_DIR = find_frontend_dir("admin_frontend")
CLIENT_DIR = find_frontend_dir("client_frontend")

if os.path.exists(ADMIN_DIR):
    app.mount("/admin", StaticFiles(directory=ADMIN_DIR, html=True), name="admin")

if os.path.exists(CLIENT_DIR):
    app.mount("/client", StaticFiles(directory=CLIENT_DIR, html=True), name="client")


@app.get("/api/v1/health", tags=["Системні"])
def health_check():
    return {"status": "online", "service": "Міністерство Запчастин API", "database": "connected"}


@app.get("/", tags=["Системні"])
def root():
    return RedirectResponse(url="/client/")
