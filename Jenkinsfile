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
                echo Cleaning workspace...
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

                rem Prevent pipeline from failing if no process found
                exit /b 0
                '''
            }
        }

        stage('📦 Setup Environment') {
            steps {
                bat '''
                echo Activating virtual environment...
                if not exist .venv (
                    echo Creating new virtual environment...
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
                echo Starting Flask app on port %FLASK_PORT%...

                start "" cmd /c "%PYTHON% src\\app.py > flask_log.txt 2>&1"
                echo Waiting for Flask to start (25s)...
                timeout /t 25 >nul

                echo --- Flask Log Preview ---
                type flask_log.txt || echo (no log found)
                echo --- End Preview ---

                echo Checking if Flask started successfully...
                curl -s http://localhost:%FLASK_PORT%/ > nul
                if %errorlevel% neq 0 (
                    echo ❌ Flask API did not respond on port %FLASK_PORT%.
                    echo ======= FLASK LOG DUMP =======
                    type flask_log.txt
                    echo ==========================================
                    exit /b 1
                )
                echo ✅ Flask API is running on port %FLASK_PORT%.
                '''
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            steps {
                bat '''
                echo Triggering Airflow DAG...
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
            echo "❌ Pipeline failed. Showing Flask logs below (if any):"
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
