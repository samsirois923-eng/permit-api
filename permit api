import json
import requests
from openai import OpenAI 


client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

def fetch_austin_permits():
    url = "https://data.austintexas.gov/resource/3syk-w9eu.json?$limit=3"
    response = requests.get(url)
    return response.json()

def normalize_permit_with_ai(raw_record):
    prompt = f"""
    Convert this raw municipal permit record into standardized JSON:
    - permit_id (string)
    - source_city (string, "Austin")
    - source_state (string, "TX")
    - issue_date (string, YYYY-MM-DD)
    - permit_type (string)
    - description (string)
    - contractor_name (string or null)
    - address (string)

    Raw Record:
    {json.dumps(raw_record)}

    Return ONLY raw JSON. No markdown formatting.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

    print("Fetching live data from Austin...")
raw_permits = fetch_austin_permits()

print("Normalizing records with AI...")
clean_permits = [normalize_permit_with_ai(r) for r in raw_permits]

with open("permits.json", "w") as f:
    json.dump(clean_permits, f, indent=2)

print("Done! Saved clean permits to permits.json")