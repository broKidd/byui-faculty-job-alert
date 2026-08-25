from playwright.sync_api import sync_playwright

FACULTY_PAGE_URL = (
    "https://wd501.myworkdaysite.com/"
    "recruiting/byui/BYU-Idaho_Faculty_Opportunities"
    "?timeType=78f926c7a502100191873747b0010000"
)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        jobs_response = None

        def handle_response(response):
            nonlocal jobs_response

            if (
                "/wday/cxs/byui/"
                "BYU-Idaho_Faculty_Opportunities/jobs"
                in response.url
            ):
                print("Found Workday jobs response!")
                print("Status:", response.status)

                if response.status == 200:
                    jobs_response = response

        page.on("response", handle_response)

        print("Opening BYU-Idaho faculty jobs page...")

        page.goto(
            FACULTY_PAGE_URL,
            wait_until="networkidle",
            timeout=60000,
        )

        # Give Workday a little extra time to finish
        # its background requests.
        page.wait_for_timeout(5000)

        if jobs_response is None:
            print("ERROR: Could not find the Workday jobs response.")
            browser.close()
            return

        data = jobs_response.json()

        print()
        print(f"Total jobs found: {data['total']}")
        print()

        for job in data["jobPostings"]:
            title = job["title"]
            job_id = job["bulletFields"][0]
            posting_end = job["bulletFields"][1]
            location = job["locationsText"]
            path = job["externalPath"]

            job_url = (
                f"https://wd501.myworkdaysite.com{path}"
            )

            print(f"Job ID: {job_id}")
            print(f"Title: {title}")
            print(f"Location: {location}")
            print(f"Posted: {job['postedOn']}")
            print(posting_end)
            print(f"URL: {job_url}")
            print("-" * 80)

        browser.close()


if __name__ == "__main__":
    main()
