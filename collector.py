import requests
import sqlite3

# Initialize Database
conn = sqlite3.connect("permits.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS permits (
    permit_number TEXT PRIMARY KEY,
    work_type TEXT,
    address TEXT,
    issue_date TEXT
)
""")
conn.commit()

# Fetch live data
URL = "https://data.austintexas.gov/resource/3syk-w9eu.json?$limit=100"
response = requests.get(URL)
data = response.json()

inserted_count = 0
if isinstance(data, list):
    for item in data:
        if isinstance(item, dict):
            permit_number = item.get("permit_number") or item.get("permit_num")
            if permit_number:
                cursor.execute("""
                INSERT OR IGNORE INTO permits (permit_number, work_type, address, issue_date)
                VALUES (?, ?, ?, ?)
                """, (
                    permit_number,
                    item.get("work_type") or item.get("permit_type_desc") or "N/A",
                    item.get("original_address1") or item.get("address") or "N/A",
                    item.get("issue_date") or item.get("issued_date") or "N/A"
                ))
                if cursor.rowcount > 0:
                    inserted_count += 1

conn.commit()
conn.close()

print(f"Done! Inserted {inserted_count} new permits into permits.db")
