import requests

WORKDAY_BASE_URL = "https://wd501.myworkdaysite.com"
WORKDAY_JOBS_URL = (
    "https://wd501.myworkdaysite.com/"
    "wday/cxs/byui/BYU-Idaho_Faculty_Opportunities/jobs"
)

FACULTY_PAGE_URL = (
    "https://wd501.myworkdaysite.com/"
    "recruiting/byui/BYU-Idaho_Faculty_Opportunities"
    "?timeType=78f926c7a502100191873747b0010000"
)


def get_jobs():
    session = requests.Session()

    # First visit the careers page.
    # This gives Workday the session cookies and CSRF token
    # that it expects for the jobs API request.
    page_response = session.get(
        FACULTY_PAGE_URL,
        headers={
            "Accept": "text/html",
            "User-Agent": "Mozilla/5.0",
        },
        timeout=30,
    )

    page_response.raise_for_status()

    # Workday places the CSRF token in this cookie.
    csrf_token = session.cookies.get("CALYPSO_CSRF_TOKEN")

    if not csrf_token:
        raise RuntimeError(
            "Could not obtain CALYPSO_CSRF_TOKEN from Workday."
        )

    payload = {
        "appliedFacets": {
            "timeType": [
                "78f926c7a502100191873747b0010000"
            ]
        },
        "limit": 100,
        "offset": 0,
        "searchText": "",
    }

    response = session.post(
        WORKDAY_JOBS_URL,
        json=payload,
        headers={
            "Accept": "application/json",
            "Accept-Language": "en-US",
            "Content-Type": "application/json",
            "Origin": WORKDAY_BASE_URL,
            "Referer": FACULTY_PAGE_URL,
            "User-Agent": "Mozilla/5.0",
            "X-Calypso-CSRF-Token": csrf_token,
        },
        timeout=30,
    )

    print("API status:", response.status_code)
    print("API response:")
    print(response.text)

    response.raise_for_status()

    return response.json()


def main():
    data = get_jobs()

    print(f"Total jobs found: {data['total']}")
    print()

    for job in data["jobPostings"]:
        title = job["title"]
        job_id = job["bulletFields"][0]
        posting_end = job["bulletFields"][1]
        location = job["locationsText"]
        path = job["externalPath"]

        job_url = f"{WORKDAY_BASE_URL}{path}"

        print(f"Job ID: {job_id}")
        print(f"Title: {title}")
        print(f"Location: {location}")
        print(f"Posted: {job['postedOn']}")
        print(posting_end)
        print(f"URL: {job_url}")
        print("-" * 80)


if __name__ == "__main__":
    main()
