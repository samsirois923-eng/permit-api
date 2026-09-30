from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader
import json
import os

app = FastAPI(title="Municipal Permits DaaS API")

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

    data = data[:limit]

    return {"count": len(data), "permits": data}

    