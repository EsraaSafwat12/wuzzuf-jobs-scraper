from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

with DAG(
    dag_id="wuzzuf_jobs_aggregation",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    truncate_table = PostgresOperator(
        task_id="truncate_jobs_by_title",
        postgres_conn_id="postgres_source",
        sql="TRUNCATE TABLE wuzzuf_jobs.jobs_by_title;",
    )

    aggregate_jobs = PostgresOperator(
        task_id="aggregate_jobs_by_title",
        postgres_conn_id="postgres_source",
        sql="""
        INSERT INTO wuzzuf_jobs.jobs_by_title (departement, jobs_count)
        SELECT
            location,
            COUNT(*) AS jobs_count
        FROM wuzzuf_jobs.jobs_raw
        WHERE location IS NOT NULL
        GROUP BY location;
        """,
    )

    truncate_table >> aggregate_jobs
