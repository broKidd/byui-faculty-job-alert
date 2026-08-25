import json
from pathlib import Path

from playwright.sync_api import sync_playwright


FACULTY_PAGE_URL = (
    "https://wd501.myworkdaysite.com/"
    "recruiting/byui/BYU-Idaho_Faculty_Opportunities"
    "?timeType=78f926c7a502100191873747b0010000"
)

BASE_URL = "https://wd501.myworkdaysite.com"

KNOWN_JOBS_FILE = Path("known_jobs.json")


def get_jobs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        jobs_response = None

        def handle_response(response):
            nonlocal jobs_response

            if (
                "/wday/cxs/byui/"
                "BYU-Idaho_Faculty_Opportunities/jobs"
                in response.url
                and response.status == 200
            ):
                jobs_response = response

        page.on("response", handle_response)

        print("Opening BYU-Idaho faculty jobs page...")

        page.goto(
            FACULTY_PAGE_URL,
            wait_until="networkidle",
            timeout=60000,
        )

        page.wait_for_timeout(5000)

        if jobs_response is None:
            browser.close()
            raise RuntimeError(
                "Could not find the Workday jobs response."
            )

        data = jobs_response.json()

        browser.close()

    jobs = []

    for job in data["jobPostings"]:
        job_id = job["bulletFields"][0]

        jobs.append(
            {
                "id": job_id,
                "title": job["title"],
                "location": job["locationsText"],
                "posted": job["postedOn"],
                "posting_end": job["bulletFields"][1],
                "url": BASE_URL + job["externalPath"],
            }
        )

    return jobs


def load_known_jobs():
    if not KNOWN_JOBS_FILE.exists():
        return {}

    with open(KNOWN_JOBS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_known_jobs(jobs):
    with open(KNOWN_JOBS_FILE, "w", encoding="utf-8") as file:
        json.dump(jobs, file, indent=2)


def main():
    jobs = get_jobs()

    print(f"Total jobs found: {len(jobs)}")

    known_jobs = load_known_jobs()

    new_jobs = []

    for job in jobs:
        if job["id"] not in known_jobs:
            new_jobs.append(job)

    print(f"Previously known jobs: {len(known_jobs)}")
    print(f"New jobs: {len(new_jobs)}")

    if new_jobs:
        print()
        print("NEW JOBS:")
        print("=" * 80)

        for job in new_jobs:
            print()
            print(job["title"])
            print(job["id"])
            print(job["posting_end"])
            print(job["url"])

    # Update the known jobs list
    all_known_jobs = {}

    for job in jobs:
        all_known_jobs[job["id"]] = job

    save_known_jobs(all_known_jobs)

    print()
    print(f"Saved {len(all_known_jobs)} jobs to {KNOWN_JOBS_FILE}")


if __name__ == "__main__":
    main()
