pipeline {
    agent any

    stages {

        stage('🧹 Clean Workspace') {
            steps {
                deleteDir()
                echo "✅ Cleaned workspace."
            }
        }

        stage('📥 Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('🐍 Setup Python Environment') {
            steps {
                bat '''
                python -m venv .venv
                call .venv\\Scripts\\activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('🧪 Test Model') {
            steps {
                bat '''
                call .venv\\Scripts\\activate
                python src\\test_model.py
                '''
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                bat '''
                echo === Deploying Flask App on port 5055 ===

                rem Kill existing Flask processes if any
                for /F "tokens=5" %%p in ('netstat -aon ^| findstr :5055 ^| findstr LISTENING') do (
                    echo Killing old Flask process %%p
                    taskkill /F /PID %%p >nul 2>&1
                )

                rem Start Flask app in background
                echo Starting Flask app...
                start "" cmd /c ".venv\\Scripts\\python.exe src\\app.py > flask_log.txt 2>&1"

                rem Wait for 20 seconds using PowerShell (works in Jenkins)
                powershell -Command "Start-Sleep -Seconds 20"

                echo --- Flask Startup Log (preview) ---
                if exist flask_log.txt type flask_log.txt | findstr /v "^$" | more
                echo ------------------------------------

                echo Checking Flask health at http://localhost:5055/
                powershell -Command "(Invoke-WebRequest -Uri 'http://localhost:5055/' -UseBasicParsing).StatusCode" > tmp_status.txt

                set /p STATUS=<tmp_status.txt
                echo Flask HTTP Status: %STATUS%

                if NOT "%STATUS%"=="200" (
                    echo ❌ Flask failed to start correctly.
                    if exist flask_log.txt type flask_log.txt
                    exit /b 1
                )

                echo ✅ Flask is running successfully on http://localhost:5055/
                '''
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            steps {
                bat '''
                echo === Triggering Airflow DAG ===
                curl -X POST "http://localhost:8080/api/v1/dags/voyage_analytics_dag/dagRuns" ^
                -H "Content-Type: application/json" ^
                -u admin:admin ^
                -d "{\\"conf\\": {\\"source\\": \\"jenkins_trigger\\"}}"
                '''
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Flask process after pipeline..."
            bat '''
            for /F "tokens=5" %%p in ('netstat -aon ^| findstr :5055 ^| findstr LISTENING') do (
                echo Stopping Flask process %%p
                taskkill /F /PID %%p >nul 2>&1
            )
            '''
        }
        failure {
            echo "❌ Pipeline failed. Showing Flask logs below (if any):"
            bat '''
            echo ========= FLASK LOG (ON FAILURE) =========
            if exist flask_log.txt type flask_log.txt
            echo ==========================================
            '''
        }
    }
}
