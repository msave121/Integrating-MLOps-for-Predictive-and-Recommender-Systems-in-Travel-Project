pipeline {
    agent any

    environment {
        PYTHON = '.venv\\Scripts\\python.exe'
        FLASK_PORT = '5055'
        AIRFLOW_USER = 'admin'
        AIRFLOW_PWD = 'admin'
        AIRFLOW_DAG_ID = 'voyage_analytics_dag'
        AIRFLOW_TRIGGER_URL = 'http://localhost:8081/api/v1/dags/voyage_analytics_dag/dagRuns'
    }

    stages {

        stage('📦 Setup Environment') {
            steps {
                echo "Setting up virtual environment..."
                bat '''
                if not exist .venv (
                    python -m venv .venv
                )
                call .venv\\Scripts\\activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('🚀 Run Flask API') {
            steps {
                echo "Starting Flask app on port %FLASK_PORT%..."

                bat '''
                rem --- Kill any old Flask processes on port ---
                "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :%FLASK_PORT% > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
                del temp_netstat.txt >nul 2>&1

                echo Starting Flask app...
                del flask_log.txt >nul 2>&1

                rem --- Run Flask in background safely ---
                start "" powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                    "cd '%cd%'; & '.venv\\Scripts\\python.exe' src\\app.py *> flask_log.txt 2>&1"

                rem --- Wait for Flask to start (PowerShell version of timeout) ---
                powershell -Command "Start-Sleep -Seconds 25"

                rem --- Health check ---
                curl -s http://localhost:%FLASK_PORT%/ >nul 2>&1
                if errorlevel 1 (
                    echo ❌ Flask failed health check!
                    echo ======= FLASK LOG =======
                    type flask_log.txt
                    echo ==========================
                    exit /b 1
                ) else (
                    echo ✅ Flask is running successfully on port %FLASK_PORT%!
                )
                '''
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            steps {
                echo "Triggering Airflow DAG..."
                bat '''
                curl -u %AIRFLOW_USER%:%AIRFLOW_PWD% ^
                    -X POST ^
                    %AIRFLOW_TRIGGER_URL% ^
                    -H "Content-Type: application/json" ^
                    -d "{\\"conf\\": {\\"triggered_by\\": \\"Jenkins Pipeline\\"}}"
                '''
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Flask process after pipeline..."
            bat '''
            "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :%FLASK_PORT% > temp_netstat.txt 2>nul
            for /F "tokens=5" %%p in (temp_netstat.txt) do (
                echo Stopping Flask process %%p
                taskkill /F /PID %%p >nul 2>&1
            )
            del temp_netstat.txt >nul 2>&1
            echo ✅ Cleanup complete.
            '''

            echo "❌ Pipeline failed. Showing Flask logs below (if any):"
            bat '''
            echo ========= FLASK LOG (ON FAILURE) =========
            if exist flask_log.txt type flask_log.txt
            echo ==========================================
            '''
        }
    }
}
