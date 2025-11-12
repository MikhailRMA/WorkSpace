from airflow.models import Connection
from airflow import settings

conn = Connection(
    conn_id='postgres_series',
    conn_type='postgres',
    host='series_tracker_project-postgres-1',
    login='postgres',
    password='password',
    port=5432,
    schema='series_tracker'
)
session = settings.Session()
session.add(conn)
session.commit()