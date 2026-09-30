from fastapi import FastAPI
import json
import os

app = FastAPI(title="Municipal Permits DaaS API")

@app.get("/")
def root():
return {"status": "online", "message": "Municipal Permits DaaS API is live"}

@app.get("/permits")
def get_permits(
zip_code: str | None = None,
work_type: str | None = None,
limit: int = 50
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

    