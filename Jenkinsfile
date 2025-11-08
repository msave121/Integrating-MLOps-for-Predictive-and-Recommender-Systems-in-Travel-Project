pipeline {
    agent any

    environment {
        PYTHON = ".venv\\Scripts\\python.exe"
        FLASK_PORT = "5055"
        FLASK_LOG = "flask_log.txt"
    }

    stages {

        stage('🧹 Cleanup Workspace') {
            steps {
                bat '''
                echo Cleaning workspace...
                if exist %FLASK_LOG% del /f /q %FLASK_LOG%

                echo Checking for existing Flask process on port %FLASK_PORT%...
                for /F "tokens=5" %%p in ('netstat -aon ^| findstr :%FLASK_PORT% ^| findstr LISTENING') do (
                    echo Killing Flask process with PID %%p
                    taskkill /F /PID %%p >nul 2>&1
                )
                echo ✅ Cleanup done.
                '''
            }
        }

        stage('📦 Setup Environment') {
            steps {
                bat '''
                echo Setting up Python environment...
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

        stage('🧪 Test Model') {
            steps {
                bat '''
                echo === Testing Regression Model ===
                call %PYTHON% src\\test_model.py
                if %ERRORLEVEL% NEQ 0 (
                    echo ❌ Model testing failed.
                    exit /b 1
                )
                echo ✅ Model tested successfully.
                '''
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                bat '''
                echo === Deploying Flask App on port %FLASK_PORT% ===

                rem Kill old Flask processes
                for /F "tokens=5" %%p in ('netstat -aon ^| findstr :%FLASK_PORT% ^| findstr LISTENING') do (
                    echo Killing old Flask process %%p
                    taskkill /F /PID %%p >nul 2>&1
                )

                rem Start Flask in background (non-blocking)
                echo Starting Flask app...
                start "" cmd /c "%PYTHON% src\\app.py > %FLASK_LOG% 2>&1"
                echo Waiting for Flask to start (25s)...
                timeout /t 25 /nobreak >nul

                echo --- Flask Log Preview (First Lines) ---
                if exist %FLASK_LOG% type %FLASK_LOG% | findstr /v "^$" | more
                echo ---------------------------------------

                echo Checking if Flask started successfully...
                curl -s http://localhost:%FLASK_PORT%/ >nul
                if %ERRORLEVEL% NEQ 0 (
                    echo ❌ Flask API did not respond on port %FLASK_PORT%.
                    echo ======= FLASK LOG DUMP =======
                    if exist %FLASK_LOG% type %FLASK_LOG%
                    echo ==========================================
                    exit /b 1
                )
                echo ✅ Flask is running successfully on port %FLASK_PORT%.
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
            if exist %FLASK_LOG% type %FLASK_LOG%
            echo ==========================================
            '''
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
    }
}
