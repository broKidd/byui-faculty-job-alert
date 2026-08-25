import requests
import json

WORKDAY_URL = "https://wd501.myworkdaysite.com/wday/cxs/byui/BYU-Idaho_Faculty_Opportunities/jobs"

payload = {
    "appliedFacets": {
        "timeType": [
            "78f926c7a502100191873747b0010000"
        ]
    },
    "limit": 100,
    "offset": 0,
    "searchText": ""
}

response = requests.post(
    WORKDAY_URL,
    json=payload,
    headers={
        "Content-Type": "application/json"
    },
    timeout=30
)

response.raise_for_status()

data = response.json()

print(f"Total jobs found: {data['total']}")
print()

for job in data["jobPostings"]:
    title = job["title"]
    job_id = job["bulletFields"][0]
    posting_end = job["bulletFields"][1]
    location = job["locationsText"]
    path = job["externalPath"]

    job_url = f"https://wd501.myworkdaysite.com{path}"

    print(f"Job ID: {job_id}")
    print(f"Title: {title}")
    print(f"Location: {location}")
    print(f"Posted: {job['postedOn']}")
    print(f"{posting_end}")
    print(f"URL: {job_url}")
    print("-" * 80)
