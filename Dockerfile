FROM mcr.microsoft.com/playwright/python:v1.55.0-noble

WORKDIR /app

RUN pip install playwright
RUN playwright install chromium

COPY byui_jobs.py .

CMD ["python", "byui_jobs.py"]
