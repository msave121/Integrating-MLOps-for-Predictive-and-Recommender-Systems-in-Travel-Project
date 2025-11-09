pipeline {
    agent any

    environment {
        PYTHON = "C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\voyage-analytics-pipeline\\.venv\\Scripts\\python.exe"
        APP_PATH = "C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\voyage-analytics-pipeline\\src\\app.py"
        PORT = "5055"

        POWERSHELL = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        NETSTAT = "C:\\Windows\\System32\\netstat.exe"
        FINDSTR = "C:\\Windows\\System32\\findstr.exe"
        PING = "C:\\Windows\\System32\\ping.exe"
    }

    stages {
        stage('📦 Checkout Code') {
            steps {
                checkout scm
                bat 'echo ✅ Code checked out from GitHub.'
            }
        }

        stage('🐍 Setup Python Environment') {
            steps {
                bat '''
                if not exist .venv (
                    echo Creating virtual environment...
                    python -m venv .venv
                )
                call .venv\\Scripts\\activate
                echo Installing dependencies...
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('🧠 Train & Test Model') {
            steps {
                bat '''
                echo Training model...
                call .venv\\Scripts\\activate
                %PYTHON% src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                echo ✅ Model trained successfully.
                echo Testing model...
                %PYTHON% src\\test_model.py
                echo ✅ Model test complete.
                '''
            }
        }

        stage('🚀 Run Flask API') {
            steps {
                bat '''
                echo === Deploying Flask App on port %PORT% ===

                rem --- Kill any process on port 5055 ---
                "%NETSTAT%" -aon | "%FINDSTR%" :%PORT% > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
                del temp_netstat.txt >nul 2>&1

                echo Starting Flask app...
                echo [Jenkins] Flask startup initiated. > flask_log.txt

                rem --- Use full PowerShell path to launch Flask ---
                "%POWERSHELL%" -NoProfile -ExecutionPolicy Bypass -Command ^
                    "cd 'C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\voyage-analytics-pipeline'; Start-Process '%PYTHON%' -ArgumentList 'src\\app.py' -RedirectStandardOutput 'flask_log.txt' -RedirectStandardError 'flask_log.txt'"

                echo Waiting for Flask to start (25 seconds)...
                "%PING%" 127.0.0.1 -n 25 >nul

                echo Checking Flask health...
                curl -s http://localhost:%PORT%/ >nul 2>&1
                if errorlevel 1 (
                    echo ❌ Flask failed health check!
                    echo ======= FLASK LOG =======
                    type flask_log.txt
                    echo ==========================
                    exit /b 1
                ) else (
                    echo ✅ Flask is running successfully on port %PORT%!
                )
                '''
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                bat '''
                echo Triggering Airflow DAG...
                curl -u admin:admin -X POST http://localhost:8080/api/v1/dags/voyage_analytics_dag/dagRuns ^
                     -H "Content-Type: application/json" ^
                     -d "{\\"conf\\": {\\"triggered_by\\": \\"jenkins\\"}}"
                '''
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up Flask process after pipeline...'
            bat '''
            "%NETSTAT%" -aon | "%FINDSTR%" :%PORT% > temp_netstat.txt 2>nul
            for /F "tokens=5" %%p in (temp_netstat.txt) do (
                echo Stopping Flask process %%p  
                taskkill /F /PID %%p >nul 2>&1
            )
            del temp_netstat.txt >nul 2>&1
            echo ✅ Cleanup complete.
            '''
        }

        failure {
            echo '❌ Pipeline failed. Showing Flask logs below (if any):'
            bat '''
            echo ========= FLASK LOG (ON FAILURE) ========= 
            if exist flask_log.txt type flask_log.txt 
            echo ==========================================
            '''
        }
    }
}
