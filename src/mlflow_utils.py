# src/mlflow_utils.py
import mlflow

def configure_mlflow(experiment_name="voyage_experiment", tracking_uri=None):
    """
    Configure MLflow tracking. If tracking_uri is provided, set it.
    Then set the experiment (creates it if missing).
    """
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
        print(f"[INFO] MLflow tracking URI set to: {tracking_uri}")
    mlflow.set_experiment(experiment_name)
    print(f"[INFO] MLflow experiment set to: {experiment_name}")

def start_run(**kwargs):
    """
    Simple wrapper returning mlflow.start_run() context manager.
    Use: with start_run() as run:
    """
    return mlflow.start_run(**kwargs)