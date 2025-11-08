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
                echo === Cleaning workspace ===
                if exist %FLASK_LOG% del /f /q %FLASK_LOG%

                echo Checking for any Flask processes on port %FLASK_PORT%...
                for /F "tokens=5" %%p in ('netstat -aon ^| findstr :%FLASK_PORT% ^| findstr LISTENING') do (
                    echo Killing old Flask process with PID %%p
                    taskkill /F /PID %%p >nul 2>&1
                )

                echo ✅ Cleanup complete.
                '''
            }
        }

        stage('📦 Setup Python Environment') {
            steps {
                bat '''
                echo === Setting up Python environment ===
                if not exist .venv (
                    echo Creating new virtual environment...
                    python -m venv .venv
                )

                call .venv\\Scripts\\activate
                echo Upgrading pip and installing dependencies...
                pip install --upgrade pip setuptools wheel
                pip install -r requirements.txt
                '''
            }
        }

        stage('🧠 Test Model') {
            steps {
                bat '''
                echo === Testing Regression Model ===
                call %PYTHON% src\\test_model.py
                if %ERRORLEVEL% NEQ 0 (
                    echo ❌ Model test failed.
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

                rem Kill any old Flask processes
                for /F "tokens=5" %%p in ('netstat -aon ^| findstr :%FLASK_PORT% ^| findstr LISTENING') do (
                    echo Killing old Flask process %%p
                    taskkill /F /PID %%p >nul 2>&1
                )

                rem Set absolute app path
                set "APP_PATH=%CD%\\src\\app.py"
                echo Using app path: %APP_PATH%

                rem Start Flask in background
                echo Starting Flask app...
                start "" cmd /c "%PYTHON% %APP_PATH% > %FLASK_LOG% 2>&1"

                echo Waiting for Flask to start (40s)...
                timeout /t 40 /nobreak >nul

                echo --- Flask Log Preview (Startup) ---
                if exist %FLASK_LOG% type %FLASK_LOG% | findstr /v "^$" | more
                echo ------------------------------------

                echo Checking Flask health on http://localhost:%FLASK_PORT%/ ...
                curl -s http://localhost:%FLASK_PORT%/ >nul

                if %ERRORLEVEL% NEQ 0 (
                    echo ❌ Flask API did not respond on port %FLASK_PORT%.
                    echo ======= FLASK LOG DUMP =======
                    if exist %FLASK_LOG% type %FLASK_LOG%
                    echo ==========================================
                    exit /b 1
                )
                echo ✅ Flask started successfully on port %FLASK_PORT%.
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
        always {
            echo "🧹 Cleaning up Flask process after pipeline..."
            bat '''
            for /F "tokens=5" %%p in ('netstat -aon ^| findstr :%FLASK_PORT% ^| findstr LISTENING') do (
                echo Stopping Flask process %%p
                taskkill /F /PID %%p >nul 2>&1
            )
            '''
        }
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
