from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2
from bs4 import BeautifulSoup


def scrape_and_insert():
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 25)

    all_jobs = []

    for page in range(0, 10):
        url = f"https://wuzzuf.net/search/jobs/?q=Data%20engineer&start={page}"
        driver.get(url)

        try:
            cards = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "css-ghe2tq"))
            )
        except Exception:
            break

        for card in cards:
            soup = BeautifulSoup(card.get_attribute("outerHTML"), "html.parser")
            title_tag = soup.find("h2")
            job_title = title_tag.text.strip() if title_tag else None
            company_tag = soup.find("a")
            company_name = company_tag.text.strip() if company_tag else None
            spans = soup.find_all("span")
            location = spans[-1].text.strip() if spans else None
            all_jobs.append((job_title, company_name, location))

    driver.quit()

    if not all_jobs:
        return

    conn = psycopg2.connect(
        host="host.docker.internal",
        dbname="source",
        user="postgres",
        password="postgres",
        port=5432,
    )
    cur = conn.cursor()

    for job in all_jobs:
        cur.execute(
            """
            INSERT INTO wuzzuf_jobs.jobs_raw
            (job_title, company_name, location, scraped_at)
            VALUES (%s, %s, %s, now())
            """,
            job,
        )

    conn.commit()
    cur.close()
    conn.close()


with DAG(
    dag_id="wuzzuf_simple_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["wuzzuf", "selenium", "scraping"],
) as dag:

    scrape_wuzzuf_jobs = PythonOperator(
        task_id="scrape_wuzzuf_jobs",
        python_callable=scrape_and_insert,
  )
