pipeline {
    agent any

    environment {
        PYTHON_HOME = "C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python312"
        VENV_DIR = ".venv"
        FLASK_PORT = "5055"
        FLASK_LOG = "flask_log.txt"
        AIRFLOW_TRIGGER = "http://localhost:8081/api/v1/dags/voyage_analytics_dag/dagRuns"
        AIRFLOW_USER = "admin"
        AIRFLOW_PASS = "admin"
    }

    stages {

        stage('🧹 Clean Workspace') {
            steps {
                deleteDir()
                echo "✅ Cleaned workspace."
            }
        }

        stage('📥 Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/msave121/msave121.git'
            }
        }

        stage('🐍 Setup Python Environment') {
            steps {
                bat '''
                echo === Setting up Python Virtual Environment ===
                set PATH=%PYTHON_HOME%;%PYTHON_HOME%\\Scripts;%PATH%
                "%PYTHON_HOME%\\python.exe" -m venv %VENV_DIR%
                call %VENV_DIR%\\Scripts\\activate
                python --version
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('🧪 Test Model') {
            steps {
                bat '''
                echo === Testing Regression Model ===
                call %VENV_DIR%\\Scripts\\activate
                python src\\test_model.py
                if %errorlevel% neq 0 (
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
                rem Kill existing Flask instances on port
                for /F "tokens=5" %%a in ('netstat -aon ^| findstr :%FLASK_PORT%') do taskkill /PID %%a /F >nul 2>&1

                rem Start Flask app (background)
                echo Starting Flask app...
                call %VENV_DIR%\\Scripts\\activate
                start "" cmd /c python src\\app.py > %FLASK_LOG% 2>&1

                rem Wait for Flask to start (check health)
                echo Waiting for Flask to start...
                powershell -Command "Start-Sleep -Seconds 10"

                powershell -Command "$r = Invoke-WebRequest -Uri http://127.0.0.1:%FLASK_PORT%/health -UseBasicParsing; if ($r.StatusCode -ne 200) { exit 1 }"
                if %errorlevel% neq 0 (
                    echo ❌ Flask failed health check!
                    type %FLASK_LOG%
                    exit /b 1
                )
                echo ✅ Flask app is running successfully on port %FLASK_PORT%.
                '''
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            steps {
                bat '''
                echo === Triggering Airflow DAG ===
                powershell -Command "Invoke-RestMethod -Method POST -Uri '%AIRFLOW_TRIGGER%' -Headers @{Authorization=('Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('%AIRFLOW_USER%:%AIRFLOW_PASS%')))} -Body '{}' "
                if %errorlevel% neq 0 (
                    echo ❌ Failed to trigger Airflow DAG.
                    exit /b 1
                )
                echo ✅ Airflow DAG triggered successfully.
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
    }
}
