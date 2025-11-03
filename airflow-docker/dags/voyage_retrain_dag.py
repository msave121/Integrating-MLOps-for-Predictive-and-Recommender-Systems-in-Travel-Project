from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import subprocess

# --- Define Python callables ---
def extract_data():
    print("✅ Extracting latest data...")
    # (Placeholder: copy new raw data / download from API)
    os.system("echo Data extraction complete")

def preprocess_data():
    print("✅ Preprocessing data...")
    os.system("python src/preprocess.py")

def train_model():
    print("✅ Training model...")
    os.system("python src/train_regression.py")

def deploy_model():
    print("✅ Updating deployment with new model...")
    # Optional: build & push Docker image (for production automation)
    subprocess.run([
        "docker", "build", "-t", "msave12345/voyage-analytics-app:latest", "."
    ])
    subprocess.run([
        "docker", "push", "msave12345/voyage-analytics-app:latest"
    ])
    print("🚀 Model re-deployed via new Docker image!")

# --- Airflow DAG definition ---
with DAG(
    dag_id="voyage_retrain_dag",
    start_date=datetime(2025, 10, 1),
    schedule_interval="@weekly",  # Run weekly (change as needed)
    catchup=False,
    tags=["voyage", "mlops"],
) as dag:

    t1 = PythonOperator(task_id="extract_data", python_callable=extract_data)
    t2 = PythonOperator(task_id="preprocess_data", python_callable=preprocess_data)
    t3 = PythonOperator(task_id="train_model", python_callable=train_model)
    t4 = PythonOperator(task_id="deploy_model", python_callable=deploy_model)

    t1 >> t2 >> t3 >> t4