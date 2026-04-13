# Wuzzuf Jobs Scraper — Airflow Pipeline

An automated data pipeline built with **Apache Airflow** that scrapes job listings from [Wuzzuf](https://wuzzuf.net), stores raw data in **PostgreSQL**, and aggregates results by location.

## Tech Stack

- Python 3.8+
- Apache Airflow
- Selenium + BeautifulSoup
- PostgreSQL
- psycopg2

## Features

- Scrapes Data Engineer job listings from Wuzzuf (10 pages)
- Extracts job title, company name, and location
- Stores raw data in PostgreSQL
- Aggregates job counts by location in a separate DAG

## Project Structure

```
wuzzuf-scraper/
│
├── dags/
│   ├── Wuzzuf.py          # Scraping DAG
│   └── wuzzuf_agg.py      # Aggregation DAG
└── README.md
```

## Pipeline Architecture

```
Wuzzuf Website
     ↓
Selenium (scrape 10 pages)
     ↓
BeautifulSoup (parse HTML)
     ↓
PostgreSQL → wuzzuf_jobs.jobs_raw
     ↓
Aggregation DAG
     ↓
PostgreSQL → wuzzuf_jobs.jobs_by_title
```

## DAGs

### 1. `wuzzuf_simple_dag` — Scraping DAG
Scrapes job listings and inserts them into the raw table.

| Field | Description |
|-------|-------------|
| job_title | Title of the job posting |
| company_name | Name of the hiring company |
| location | Job location |
| scraped_at | Timestamp of when the record was scraped |

### 2. `wuzzuf_jobs_aggregation` — Aggregation DAG
Aggregates job counts grouped by location.

| Field | Description |
|-------|-------------|
| departement | Location / area |
| jobs_count | Number of job postings in that location |

## Database Setup

```sql
CREATE SCHEMA wuzzuf_jobs;

CREATE TABLE wuzzuf_jobs.jobs_raw (
    id SERIAL PRIMARY KEY,
    job_title TEXT,
    company_name TEXT,
    location TEXT,
    scraped_at TIMESTAMP
);

CREATE TABLE wuzzuf_jobs.jobs_by_title (
    departement TEXT,
    jobs_count INTEGER
);
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/wuzzuf-scraper.git
cd wuzzuf-scraper
```

### 2. Install dependencies

```bash
pip install apache-airflow selenium beautifulsoup4 psycopg2-binary
```

### 3. Configure PostgreSQL connection in Airflow

Set up a connection named `postgres_source` in Airflow UI with your PostgreSQL credentials.

### 4. Place DAGs in your Airflow DAGs folder

```bash
cp dags/* ~/airflow/dags/
```

### 5. Run the DAGs

Trigger `wuzzuf_simple_dag` first, then `wuzzuf_jobs_aggregation`.

