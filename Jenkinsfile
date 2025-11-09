pipeline {
    agent any

    environment {
        PYTHON = ".venv\\Scripts\\python.exe"
        FLASK_PORT = "5055"
        NETSTAT = "C:\\Windows\\System32\\netstat.exe"
        FINDSTR = "C:\\Windows\\System32\\findstr.exe"
        POWERSHELL = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        TIMEOUT = "C:\\Windows\\System32\\timeout.exe"
        WORKSPACE_DIR = "C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\voyage-analytics-pipeline"
        FLASK_LOG = "C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\voyage-analytics-pipeline\\flask_log.txt"
    }

    stages {
        stage('📦 Setup Environment') {
            steps {
                echo "Setting up Python virtual environment..."
                bat """
                if not exist .venv (
                    python -m venv .venv
                )
                call .venv\\Scripts\\activate
                pip install --upgrade pip
                pip install -r requirements.txt
                """
            }
        }

        stage('🧠 Train Model') {
            steps {
                echo "Training regression model..."
                bat """
                call .venv\\Scripts\\activate
                %PYTHON% src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                """
            }
        }

        stage('🚀 Deploy Flask API') {
            steps {
                echo "=== Deploying Flask App on port %FLASK_PORT% ==="

                bat """
                rem --- Kill existing process on port 5055 ---
                "%NETSTAT%" -aon | "%FINDSTR%" :%FLASK_PORT% > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
                del temp_netstat.txt >nul 2>&1

                rem --- Start Flask in background ---
                echo Starting Flask app...
                del "%FLASK_LOG%" >nul 2>&1

                "%POWERSHELL%" -NoProfile -ExecutionPolicy Bypass -Command ^
                    "cd '%WORKSPACE_DIR%'; Start-Process '%PYTHON%' 'src\\app.py' -NoNewWindow -RedirectStandardOutput '%FLASK_LOG%' -RedirectStandardError '%FLASK_LOG%'"

                rem --- Wait for Flask to start ---
                echo Waiting up to 25 seconds for Flask to start...
                "%TIMEOUT%" /t 25 /nobreak >nul

                rem --- Health check ---
                curl -s http://localhost:%FLASK_PORT%/ >nul 2>&1
                if errorlevel 1 (
                    echo ❌ Flask failed health check!
                    echo ======= FLASK LOG =======
                    if exist "%FLASK_LOG%" type "%FLASK_LOG%"
                    echo ==========================
                    exit /b 1
                ) else (
                    echo ✅ Flask is running successfully on port %FLASK_PORT%!
                )
                """
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            when {
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                echo "Triggering Airflow DAG..."
                bat """
                curl -X POST http://localhost:8080/api/v1/dags/voyage_analytics_dag/dagRuns ^
                     -H "Content-Type: application/json" ^
                     -u admin:admin ^
                     -d "{\\"conf\\": {\\"triggered_by\\": \\"Jenkins Pipeline\\"}}"
                """
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Flask process after pipeline..."
            bat """
            "%NETSTAT%" -aon | "%FINDSTR%" :%FLASK_PORT% > temp_netstat.txt 2>nul
            for /F "tokens=5" %%p in (temp_netstat.txt) do (
                echo Stopping Flask process %%p
                taskkill /F /PID %%p >nul 2>&1
            )
            del temp_netstat.txt >nul 2>&1
            """

            echo "✅ Cleanup complete."
        }

        failure {
            echo "❌ Pipeline failed. Showing Flask logs below (if any):"
            bat """
            echo ========= FLASK LOG (ON FAILURE) =========
            if exist "%FLASK_LOG%" type "%FLASK_LOG%"
            echo ==========================================
            """
        }
    }
}
