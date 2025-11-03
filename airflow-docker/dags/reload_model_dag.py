from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def reload_model():
    print("🔁 Reloading the latest model or restarting the container...")
    # You can expand this to actually reload your model in a running API if needed.

with DAG(
    dag_id="reload_model_dag",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["deployment"],
) as dag:
    reload = PythonOperator(
        task_id="reload_model_task",
        python_callable=reload_model
    )
