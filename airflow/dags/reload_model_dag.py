from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import os

# --- DAG Configuration ---
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

# --- Define Python Tasks ---

def reload_model():
    """Simulate reloading the latest ML model from storage or Docker."""
    print("🔁 Reloading the latest Voyage Analytics model...")
    # Example placeholder logic — replace with your actual model update steps
    model_path = "/opt/airflow/models/voyage_model.pkl"
    if os.path.exists(model_path):
        print(f"✅ Model found at {model_path}. Reloading complete.")
    else:
        print("⚠ Model not found. Please verify model upload location.")
    return "Reload successful."

def notify_jenkins():
    """Notify Jenkins or logging system after reload"""
    print("📡 Sending callback or logging notification to Jenkins...")
    # Optional callback (disabled by default)
    # requests.post("http://jenkins.local/job/notify_reload", data={"status": "success"})

# --- DAG Definition ---
with DAG(
    dag_id="reload_model_dag",
    default_args=default_args,
    schedule_interval=None,  # Trigger manually via API
    catchup=False,
    tags=["voyage", "mlops", "jenkins"],
) as dag:

    reload_model_task = PythonOperator(
        task_id="reload_model_task",
        python_callable=reload_model,
    )

    notify_jenkins_task = PythonOperator(
        task_id="notify_jenkins_task",
        python_callable=notify_jenkins,
    )

    reload_model_task >> notify_jenkins_task
