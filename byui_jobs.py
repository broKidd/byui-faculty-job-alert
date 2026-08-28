import os
import smtplib
from email.message import EmailMessage

from playwright.sync_api import sync_playwright


# ============================================================
# SETTINGS
# ============================================================

FACULTY_PAGE_URL = (
    "https://wd501.myworkdaysite.com/"
    "recruiting/byui/BYU-Idaho_Faculty_Opportunities"
    "?timeType=78f926c7a502100191873747b0010000"
)

# Correct base URL for individual job postings
BASE_URL = (
    "https://wd501.myworkdaysite.com"
    "/en-US/recruiting/byui/BYU-Idaho_Faculty_Opportunities"
)

# Email recipient
RECIPIENT_EMAIL = os.environ["YAHOO_EMAIL"]


# ============================================================
# KEYWORD PRIORITIES
# ============================================================

KEYWORDS = {
    # Highest priority
    "web development": 10,
    "software": 10,
    "computer science": 10,
    "programming": 10,

    # Very high priority
    "engineering": 9,
    "computer": 9,

    # High priority
    "web": 8,
    "development": 8,
    "artificial intelligence": 8,
    "machine learning": 8,

    # Medium priority
    "information systems": 6,
    "information technology": 6,
    "technology": 6,

    # Lower priority
    "data": 5,
    "cybersecurity": 5,
    "database": 5,
    "databases": 5,
    "network": 5,
    "networking": 5,

    # Programming languages / technologies
    "javascript": 10,
    "python": 10,
    "java": 10,
    "react": 10,
    "typescript": 10,
}


# ============================================================
# GET JOBS FROM WORKDAY
# ============================================================

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

        # Give Workday additional time to finish loading.
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

        jobs.append(
            {
                "id": job["bulletFields"][0],
                "title": job["title"],
                "location": job["locationsText"],
                "posted": job["postedOn"],
                "posting_end": job["bulletFields"][1],
                "url": BASE_URL + job["externalPath"],
            }
        )

    return jobs


# ============================================================
# CALCULATE JOB PRIORITY
# ============================================================

def calculate_priority(job):

    title = job["title"].lower()

    score = 0
    matched_keywords = []

    for keyword, points in KEYWORDS.items():

        if keyword.lower() in title:

            score += points

            matched_keywords.append(keyword)

    return score, matched_keywords


# ============================================================
# SORT JOBS
# ============================================================

def prioritize_jobs(jobs):

    for job in jobs:

        score, matched_keywords = calculate_priority(job)

        job["priority"] = score
        job["matched_keywords"] = matched_keywords

    # Highest priority first.
    #
    # Jobs with the same score are sorted alphabetically.
    jobs.sort(
        key=lambda job: (
            -job["priority"],
            job["title"].lower()
        )
    )

    return jobs


# ============================================================
# SEND EMAIL
# ============================================================

def send_email(jobs):

    gmail_username = os.environ["GMAIL_USERNAME"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]

    message = EmailMessage()

    message["Subject"] = (
        f"BYU-Idaho Faculty Job Openings "
        f"({len(jobs)} positions)"
    )

    message["From"] = gmail_username
    message["To"] = RECIPIENT_EMAIL


    # ========================================================
    # PLAIN TEXT EMAIL
    # ========================================================

    text = "BYU-IDAHO FACULTY JOB OPENINGS\n\n"

    text += (
        f"{len(jobs)} current full-time faculty positions.\n"
    )

    text += (
        "Jobs matching your preferred technology, "
        "software, development, computer, and engineering "
        "keywords are listed first.\n\n"
    )

    for job in jobs:

        if job["priority"] > 0:

            text += "⭐ PRIORITY MATCH\n"

        text += f"{job['title']}\n"
        text += f"Job ID: {job['id']}\n"
        text += f"Location: {job['location']}\n"
        text += f"{job['posting_end']}\n"

        if job["matched_keywords"]:

            text += (
                "Matched keywords: "
                + ", ".join(job["matched_keywords"])
                + "\n"
            )

        text += f"{job['url']}\n"

        text += "\n" + "-" * 70 + "\n\n"

    message.set_content(text)


    # ========================================================
    # HTML EMAIL
    # ========================================================

    html = """
    <html>

    <body style="
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
    ">

        <h2>BYU-Idaho Faculty Job Openings</h2>

        <p>
            Here are the current full-time faculty positions
            listed by BYU-Idaho.
        </p>

        <p>
            <strong>⭐ Priority jobs</strong> are positions
            matching your technology, software, development,
            computer, engineering, and related keywords.
        </p>
    """


    for job in jobs:

        # ====================================================
        # PRIORITY JOB
        # ====================================================

        if job["priority"] > 0:

            html += f"""

            <div style="
                border: 2px solid #f0b400;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                background-color: #fffdf2;
            ">

                <div style="
                    font-weight: bold;
                    color: #b07800;
                    margin-bottom: 8px;
                ">
                    ⭐ PRIORITY MATCH
                </div>

                <h3 style="margin-top: 0;">
                    {job['title']}
                </h3>

                <p>
                    <strong>Job ID:</strong> {job['id']}<br>

                    <strong>Location:</strong>
                    {job['location']}<br>

                    <strong>{job['posting_end']}</strong>
                </p>

                <p>
                    <strong>Matched keywords:</strong>
                    {", ".join(job["matched_keywords"])}
                </p>

                <p>
                    <a
                        href="{job['url']}"
                        style="
                            display: inline-block;
                            padding: 10px 15px;
                            background-color: #0066cc;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                        "
                    >
                        View Job Posting
                    </a>
                </p>

            </div>
            """


        # ====================================================
        # NORMAL JOB
        # ====================================================

        else:

            html += f"""

            <div style="
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            ">

                <h3 style="margin-top: 0;">
                    {job['title']}
                </h3>

                <p>
                    <strong>Job ID:</strong> {job['id']}<br>

                    <strong>Location:</strong>
                    {job['location']}<br>

                    <strong>{job['posting_end']}</strong>
                </p>

                <p>
                    <a
                        href="{job['url']}"
                        style="
                            display: inline-block;
                            padding: 10px 15px;
                            background-color: #0066cc;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                        "
                    >
                        View Job Posting
                    </a>
                </p>

            </div>
            """


    # ========================================================
    # EMAIL FOOTER
    # ========================================================

    html += """

        <p style="
            color: #777;
            font-size: 12px;
            margin-top: 25px;
        ">
            This email was automatically generated by the
            BYU-Idaho Faculty Job Alert.
        </p>

    </body>

    </html>
    """


    message.add_alternative(
        html,
        subtype="html"
    )


    # ========================================================
    # SEND THROUGH GMAIL
    # ========================================================

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:

        smtp.login(
            gmail_username,
            gmail_password
        )

        smtp.send_message(message)


    print(
        f"Email sent successfully to "
        f"{RECIPIENT_EMAIL}!"
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    jobs = get_jobs()

    print(
        f"Total jobs found: {len(jobs)}"
    )

    if not jobs:

        print(
            "No jobs found. "
            "Email will not be sent."
        )

        return

    print(
        "Calculating job priorities..."
    )

    jobs = prioritize_jobs(jobs)

    # Show priority results in GitHub Actions
    for job in jobs:

        if job["priority"] > 0:

            print(
                f"PRIORITY {job['priority']}: "
                f"{job['title']} "
                f"({', '.join(job['matched_keywords'])})"
            )

    print(
        "Sending job list..."
    )

    send_email(jobs)


if __name__ == "__main__":

    main()
