pipeline {
    agent any

    environment {
        PYTHON = ".venv\\Scripts\\python.exe"
        FLASK_PORT = "5055"
    }

    stages {

        stage('🧹 Cleanup Workspace') {
            steps {
                bat '''
                echo === Cleaning workspace ===
                if exist flask_log.txt del /f /q flask_log.txt

                echo Checking for any existing Flask processes on port %FLASK_PORT%...
                set "FOUND_PROCESS="
                for /f "tokens=5" %%p in ('netstat -aon ^| findstr :%FLASK_PORT% ^| findstr LISTENING') do (
                    echo Killing old Flask process with PID %%p
                    taskkill /F /PID %%p
                    set FOUND_PROCESS=1
                )

                if not defined FOUND_PROCESS (
                    echo ✅ No existing Flask process found on port %FLASK_PORT%.
                ) else (
                    echo 🔁 Existing Flask process killed successfully.
                )

                rem Prevent pipeline from failing if nothing found
                exit /b 0
                '''
            }
        }

        stage('📦 Setup Environment') {
            steps {
                bat '''
                echo === Setting up Python environment ===
                if not exist .venv (
                    echo Creating virtual environment...
                    python -m venv .venv
                )
                call .venv\\Scripts\\activate
                echo Installing dependencies...
                pip install --upgrade pip setuptools wheel
                pip install -r requirements.txt
                '''
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                bat '''
                echo === Starting Flask App ===
                del flask_log.txt 2>nul

                echo Launching Flask on port %FLASK_PORT%...
                start "" cmd /c "call .venv\\Scripts\\activate && python src\\app.py > flask_log.txt 2>&1"

                echo Waiting 15 seconds for Flask to start...
                ping 127.0.0.1 -n 15 >nul

                echo Checking health of Flask app...
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
                echo === Triggering Airflow DAG ===
                curl -X POST http://localhost:8081/api/v1/dags/voyage_analytics_dag/dagRuns ^
                     -H "Content-Type: application/json" ^
                     -u admin:admin ^
                     -d "{\\"conf\\": {\\"run_type\\": \\"jenkins\\"}}"
                '''
            }
        }
    }

    post {
        failure {
            echo "❌ Pipeline failed. Showing Flask logs (if any):"
            bat '''
            echo ========= FLASK LOG (ON FAILURE) =========
            if exist flask_log.txt type flask_log.txt
            echo ==========================================
            '''
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
    }
}
