import sqlite3
from typing import Optional
from fastapi import FastAPI, Query, Security, HTTPException, status
from fastapi.security import APIKeyHeader

app = FastAPI(title="Municipal Permits DaaS API", version="1.0.0")

# Secret API key for authentication
VALID_API_KEYS = {"my-secret-key-123"}
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return api_key

def get_db_connection():
    conn = sqlite3.connect("permits.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/v1/permits")
def get_permits(
    work_type: Optional[str] = Query(None, description="Filter by work type"),
    limit: int = Query(50, ge=1, le=500, description="Number of permits to return"),
    api_key: str = Security(verify_api_key)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT permit_number, work_type, address, issue_date FROM permits"
    params = []

    if work_type:
        query += " WHERE LOWER(work_type) LIKE ?"
        params.append(f"%{work_type.lower()}%")

    query += " LIMIT ?"
    params.append(limit)

    rows = cursor.execute(query, params).fetchall()
    conn.close()

    return [dict(row) for row in rows]
