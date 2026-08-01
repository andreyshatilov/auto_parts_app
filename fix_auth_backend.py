import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Update models.py
with open('backend/app/models.py', 'r', encoding='utf-8') as f:
    models_code = f.read()

# Add hashed_password and is_verified to Client
client_mod = r"""    has_messenger = Column(Boolean, default=True, nullable=False)
    shipping_address = Column(Text, nullable=True)"""
client_mod_new = r"""    has_messenger = Column(Boolean, default=True, nullable=False)
    shipping_address = Column(Text, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)"""
models_code = models_code.replace(client_mod, client_mod_new)

# Add OTPCode class at the end
otp_class = r"""

class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(100), index=True, nullable=False)
    code = Column(String(10), nullable=False)
    expires_at = Column(DateTime, nullable=False)
"""
if "class OTPCode" not in models_code:
    models_code += otp_class

with open('backend/app/models.py', 'w', encoding='utf-8') as f:
    f.write(models_code)


# 2. Update schemas.py
with open('backend/app/schemas.py', 'r', encoding='utf-8') as f:
    schemas_code = f.read()

client_create_old = r"""class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    has_messenger: Optional[bool] = True"""
client_create_new = r"""class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    password: str
    has_messenger: Optional[bool] = True"""
schemas_code = schemas_code.replace(client_create_old, client_create_new)

client_resp_old = r"""class ClientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None
    has_messenger: bool
    shipping_address: Optional[str] = None
    auth_token: str"""
client_resp_new = r"""class ClientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None
    has_messenger: bool
    is_verified: bool
    shipping_address: Optional[str] = None
    auth_token: str"""
schemas_code = schemas_code.replace(client_resp_old, client_resp_new)

if "class VerifyOTP(" not in schemas_code:
    schemas_code += """

class VerifyOTP(BaseModel):
    email: str
    code: str

class ForgotPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    email: str
    code: str
    new_password: str

class LoginRequest(BaseModel):
    phone_or_email: str
    password: str
"""

with open('backend/app/schemas.py', 'w', encoding='utf-8') as f:
    f.write(schemas_code)


# 3. Update main.py for migration
with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    main_code = f.read()

migration_old = r"""            ("generation", "VARCHAR(50)"),
            ("body_type", "VARCHAR(50)"),
            ("fuel_type", "VARCHAR(50)"),
            ("horse_power", "VARCHAR(50)"),
            ("color_code", "VARCHAR(50)"),
            ("assembly_plant", "VARCHAR(100)"),
            ("custom_photo_url", "VARCHAR(255)"),
            ("notes", "TEXT")
        ]
        for c_name, c_type in cols:
            try:
                conn.execute(text(f"ALTER TABLE cars ADD COLUMN {c_name} {c_type};"))
                conn.commit()
            except Exception:
                conn.rollback()"""
                
migration_new = r"""            ("generation", "VARCHAR(50)"),
            ("body_type", "VARCHAR(50)"),
            ("fuel_type", "VARCHAR(50)"),
            ("horse_power", "VARCHAR(50)"),
            ("color_code", "VARCHAR(50)"),
            ("assembly_plant", "VARCHAR(100)"),
            ("custom_photo_url", "VARCHAR(255)"),
            ("notes", "TEXT")
        ]
        for c_name, c_type in cols:
            try:
                conn.execute(text(f"ALTER TABLE cars ADD COLUMN {c_name} {c_type};"))
                conn.commit()
            except Exception:
                conn.rollback()
                
        client_cols = [
            ("hashed_password", "VARCHAR(255)"),
            ("is_verified", "BOOLEAN DEFAULT FALSE")
        ]
        for c_name, c_type in client_cols:
            try:
                conn.execute(text(f"ALTER TABLE clients ADD COLUMN {c_name} {c_type};"))
                conn.commit()
            except Exception:
                conn.rollback()
                
        # Make existing valid emails verified by default to avoid blocking existing good users
        try:
            conn.execute(text("UPDATE clients SET is_verified = TRUE WHERE email IS NOT NULL AND hashed_password IS NULL;"))
            conn.commit()
        except Exception:
            conn.rollback()"""

if "hashed_password" not in main_code:
    main_code = main_code.replace(migration_old, migration_new)
with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(main_code)

print("Backend schema and migrations updated.")
