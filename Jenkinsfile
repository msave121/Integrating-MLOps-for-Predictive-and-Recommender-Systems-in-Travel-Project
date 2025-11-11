pipeline {
    agent any

    environment {
        PYTHON = ".venv\\Scripts\\python.exe"
        FLASK_PORT = "5055"
        AIRFLOW_USER = "admin"
        AIRFLOW_PASS = "admin"
    }

    stages {

        stage('🧹 Clean Up') {
            steps {
                bat '''
                echo Cleaning workspace...
                if exist flask_log.txt del /f /q flask_log.txt

                echo Checking for any existing Flask processes on port %FLASK_PORT%...
                for /f "tokens=5" %%p in ('netstat -aon ^| findstr :%FLASK_PORT% ^| findstr LISTENING') do (
                    echo Killing old Flask process with PID %%p
                    taskkill /F /PID %%p
                )
                exit /b 0
                '''
            }
        }

        stage('⚙️ Setup Python Env') {
            steps {
                bat '''
                echo Setting up virtual environment...
                if not exist .venv (
                    python -m venv .venv
                )
                call .venv\\Scripts\\activate
                echo Installing dependencies...
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('🚀 Start Flask App') {
            steps {
                bat '''
                echo Starting Flask app on port %FLASK_PORT%...
                del flask_log.txt 2>nul
                start "" cmd /c "call .venv\\Scripts\\activate && python src\\app.py > flask_log.txt 2>&1"

                echo Waiting 15 seconds for Flask to start...
                timeout /t 15 >nul

                echo Checking health...
                curl -s http://localhost:%FLASK_PORT% >nul
                if errorlevel 1 (
                    echo ❌ Flask failed to start!
                    if exist flask_log.txt type flask_log.txt
                    exit /b 1
                ) else (
                    echo ✅ Flask is running successfully on port %FLASK_PORT%!
                )
                '''
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            steps {
                bat '''
                echo Triggering Airflow DAG...
                curl -X POST http://localhost:8081/api/v1/dags/voyage_analytics_dag/dagRuns ^
                     -H "Content-Type: application/json" ^
                     -u %AIRFLOW_USER%:%AIRFLOW_PASS% ^
                     -d "{\\"conf\\": {\\"run_type\\": \\"jenkins\\"}}"
                '''
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning Flask process..."
            bat '''
            for /f "tokens=5" %%p in ('netstat -aon ^| findstr :%FLASK_PORT% ^| findstr LISTENING') do (
                taskkill /F /PID %%p
            )
            exit /b 0
            '''
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed. Showing Flask logs:"
            bat '''
            if exist flask_log.txt type flask_log.txt
            '''
        }
    }
}
