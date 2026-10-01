from fastapi import FastAPI, Depends, HTTPException, status, Security, Request
from fastapi.security.api_key import APIKeyHeader
import json
import os
import secrets
import stripe

app = FastAPI(title="Municipal Permits DaaS API")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
stripe.api_key = STRIPE_SECRET_KEY

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

VALID_API_KEYS = {
    "test_key_12345": "Beta User",
    "permits_secret_999": "Paying Customer"
}

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key in VALID_API_KEYS:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key. Please pass a valid 'X-API-Key' header."
    )

@app.get("/")
def root():
    return {"status": "online", "message": "Municipal Permits DaaS API is live"}

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_details", {}).get("email", "Unknown")

        new_key = f"pk_live_{secrets.token_urlsafe(16)}"
        VALID_API_KEYS[new_key] = customer_email

        print(f"SUCCESS: Generated key '{new_key}' for customer: {customer_email}")

    return {"status": "success"}

@app.get("/permits")
def get_permits(
    zip_code: str | None = None,
    work_type: str | None = None,
    limit: int = 50,
    api_key: str = Depends(get_api_key)
):
    if not os.path.exists("permits.json"):
        return {"error": "No permit data found"}

    with open("permits.json", "r") as f:
        data = json.load(f)

    if zip_code:
        data = [
            p for p in data 
            if zip_code in str(p.get("address", "")) or zip_code == str(p.get("zip_code", ""))
        ]

    if work_type:
        data = [
            p for p in data 
            if work_type.lower() in str(p.get("work_type", "")).lower()
        ]

    return {"count": len(data[:limit]), "permits": data[:limit]}
import os
import uuid
import stripe
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Triggered when checkout completes successfully
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # Generate new API key
        new_api_key = f"sk_live_{uuid.uuid4().hex}"
        
        # Log key so you can copy it from Render logs
        print(f"=== NEW GENERATED API KEY: {new_api_key} ===", flush=True)

    return {"status": "success"}
    