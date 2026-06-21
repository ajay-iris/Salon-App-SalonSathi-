from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import string
import uvicorn
from twilio.rest import Client

# --- PostgreSQL Engine Modules ---
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Integer

app = FastAPI()

# 1. Database Connection String Configuration (Updated to test_db)
DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5432/test_db"

async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# 2. Define Table Database Models Schemas (Updated to match user_info)
class UserModel(Base):
    __tablename__ = "user_info"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)  # Matches your SQL 'username' column

class OTPModel(Base):
    __tablename__ = "active_otps"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    code = Column(String, nullable=False)

# Auto-initialize and generate tables on application boot if they don't exist
@app.on_event("startup")
async def startup_event():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- Twilio SMS Stub Infrastructure ---
TWILIO_ACCOUNT_SID = "your_twilio_account_sid_here"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token_here"
TWILIO_SENDER_NUMBER = "+1234567890"

def transmit_real_sms(target_phone: str, verification_code: str):
    try:
        if "your_" in TWILIO_ACCOUNT_SID:
            print(f"\n[FALLBACK LOG] Target Code for {target_phone}: {verification_code}\n")
            return True
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=f"Code: {verification_code}", from_=TWILIO_SENDER_NUMBER, to=target_phone)
        return True
    except Exception:
        return False

# --- Pydantic Data Validation Schemas ---
class OTPRequest(BaseModel):
    phone: str
    purpose: str

class RegistrationPayload(BaseModel):
    phone: str
    name: str  # Kept as 'name' to receive from Flet frontend payload cleanly
    otp_code: str

class LoginPayload(BaseModel):
    phone: str
    otp_code: str

# --- PostgreSQL API Endpoint Logic Engines ---

@app.post("/api/auth/request-otp")
async def request_otp_routing(payload: OTPRequest):
    phone = payload.phone.strip()
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        user_query = await session.execute(select(UserModel).where(UserModel.phone == phone))
        existing_profile = user_query.scalar_one_or_none()

        if payload.purpose == "login" and not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not registered. Please create an account first.")
        if payload.purpose == "registration" and existing_profile:
            raise HTTPException(status_code=400, detail="This phone number is already registered.")

        secure_otp = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

        otp_query = await session.execute(select(OTPModel).where(OTPModel.phone == phone))
        existing_otp = otp_query.scalar_one_or_none()

        if existing_otp:
            existing_otp.code = secure_otp
        else:
            new_otp_record = OTPModel(phone=phone, code=secure_otp)
            session.add(new_otp_record)
        
        await session.commit()

    transmit_real_sms(phone, secure_otp)
    return {"status": "success", "message": "Verification code transmitted successfully."}


@app.post("/api/auth/register-user")
async def register_user_pipeline(payload: RegistrationPayload):
    phone = payload.phone.strip()
    from sqlalchemy import select, delete

    async with AsyncSessionLocal() as session:
        otp_query = await session.execute(select(OTPModel).where(OTPModel.phone == phone))
        otp_record = otp_query.scalar_one_or_none()

        if not otp_record or otp_record.code != payload.otp_code.upper():
            raise HTTPException(status_code=401, detail="Security Mismatch: Code is invalid or expired.")

        await session.execute(delete(OTPModel).where(OTPModel.phone == phone))

        user_query = await session.execute(select(UserModel).where(UserModel.phone == phone))
        user_profile = user_query.scalar_one_or_none()

        if user_profile:
            user_profile.username = payload.name.strip()  # Maps frontend name input to database username column
        else:
            new_user = UserModel(phone=phone, username=payload.name.strip())
            session.add(new_user)

        await session.commit()
    
    return {"status": "success", "message": "Account created successfully!"}


@app.post("/api/auth/verify-login")
async def verify_login_pipeline(payload: LoginPayload):
    phone = payload.phone.strip()
    from sqlalchemy import select, delete

    async with AsyncSessionLocal() as session:
        otp_query = await session.execute(select(OTPModel).where(OTPModel.phone == phone))
        otp_record = otp_query.scalar_one_or_none()

        if not otp_record or otp_record.code != payload.otp_code.upper():
            raise HTTPException(status_code=401, detail="Security Mismatch: Code is invalid or expired.")

        user_query = await session.execute(select(UserModel).where(UserModel.phone == phone))
        user_profile = user_query.scalar_one_or_none()

        if not user_profile:
            raise HTTPException(status_code=404, detail="Database lookup mismatch error.")

        await session.execute(delete(OTPModel).where(OTPModel.phone == phone))
        await session.commit()

        return {
            "status": "success",
            "user_profile": {"phone": user_profile.phone, "name": user_profile.username} # Passes username back as name to Flet app
        }

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)