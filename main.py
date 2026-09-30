from fastapi import FastAPI
import json
import os

app = FastAPI(title="Municipal Permits DaaS API")

@app.get("/")
def root():
    return {"status": "online", "message": "Municipal Permits DaaS API is live"}

@app.get("/permits")
def get_permits():
    if os.path.exists("permits.json"):
        with open("permits.json", "r") as f:
            data = json.load(f)
        return {"count": len(data), "permits": data}
    return {"error": "No permit data found"}
    