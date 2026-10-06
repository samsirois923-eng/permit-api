import uuid
from datetime import datetime
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.security import APIKeyHeader
from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./keys.db"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class APIKey(Base):
    __tablename__ = "api_keys"

    key = Column(String, primary_key=True, index=True)
    customer_email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI()
apiKeyHeader = APIKeyHeader(name="X-API-Key", auto_error=False)


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.json()

    # Extract customer email from Stripe event object
    customer_email = (
        payload.get("data", {})
        .get("object", {})
        .get("customer_details", {})
        .get("email")
        or "unknown@example.com"
    )

    db = SessionLocal()
    new_key = f"sk_live_{uuid.uuid4().hex}"

    db_key = APIKey(key=new_key, customer_email=customer_email)
    db.add(db_key)
    db.commit()
    db.close()

    print(f"=== STORED NEW API KEY FOR {customer_email}: {new_key} ===", flush=True)
    return {"status": "success", "key": new_key}


@app.get("/permits")
def get_permits(limit: int = 50, x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API Key")

    db = SessionLocal()
    existing_key = db.query(APIKey).filter(APIKey.key == x_api_key).first()
    db.close()

    if not existing_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return {"permits": [{"id": 1, "type": "Building", "status": "Approved"}]}

    