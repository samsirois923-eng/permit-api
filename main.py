import os
import uuid
from fastapi import FastAPI, Header, HTTPException, Request
import stripe
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

stripe.api_key = STRIPE_SECRET_KEY

DATABASE_URL = "sqlite:///./keys.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class APIKey(Base):
    __tablename__ = "api_keys"
    key = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/permits")
def get_permits(x_api_key: str = Header(None)):
    db = SessionLocal()
    try:
        key_record = db.query(APIKey).filter(APIKey.key == x_api_key).first()
        if not key_record:
            raise HTTPException(status_code=401, detail="Invalid API Key")
    finally:
        db.close()

    return [
        {"id": 1, "permit_number": "PERMIT-2026-001", "type": "Building", "status": "Approved"},
        {"id": 2, "permit_number": "PERMIT-2026-002", "type": "Electrical", "status": "Pending"}
    ]


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_dict = event.to_dict()

    if event_dict.get('type') == 'checkout.session.completed':
        session = event_dict.get('data', {}).get('object', {})
        customer_email = session.get('customer_details', {}).get('email') or session.get('customer_email')

        new_key = f"pk_live_{uuid.uuid4().hex}"

        db = SessionLocal()
        try:
            db_key = APIKey(key=new_key, email=customer_email)
            db.add(db_key)
            db.commit()
            print(f"Generated API Key: {new_key} for {customer_email}")
        finally:
            db.close()

    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)




    