Code in VS Code (main.py)
Replace everything in main.py with this exact code and save the file (Cmd+S or Ctrl+S):

Python
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.security import APIKeyHeader
import stripe
import uuid

app = FastAPI()

# Store valid API keys
VALID_KEYS = set()

apiKeyHeader = APIKeyHeader(name="X-API-Key", auto_error=False)

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    new_key = f"sk_live_{uuid.uuid4().hex}"
    VALID_KEYS.add(new_key)
    print(f"=== NEW GENERATED API KEY: {new_key} ===", flush=True)
    return {"status": "success", "key": new_key}

@app.get("/permits")
def get_permits(limit: int = 50, x_api_key: str = Header(None)):
    if not x_api_key or x_api_key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return {"permits": [{"id": 1, "type": "Building", "status": "Approved"}]}

    