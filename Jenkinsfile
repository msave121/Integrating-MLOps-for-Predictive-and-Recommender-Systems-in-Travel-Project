pipeline {
    agent any

    environment {
        FLASK_PORT = '5055'
        VENV_PATH  = '.venv\\Scripts\\activate'
    }

    stages {

        stage('🧰 Setup Python Env') {
            steps {
                bat '''
                echo === Setting up virtual environment ===
                if not exist .venv (
                    echo Creating venv...
                    python -m venv .venv
                )
                call %VENV_PATH%
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('🧪 Run Tests') {
            steps {
                bat '''
                echo === Running tests ===
                call %VENV_PATH%
                pytest -v || exit /b 1
                '''
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                bat '''
                echo === Starting Flask App ===
                del flask_log.txt 2>nul

                echo Launching Flask on port %FLASK_PORT%...
                start "" cmd /c "call %VENV_PATH% && python src\\app.py > flask_log.txt 2>&1"

                echo Waiting for Flask to fully start (up to 60 seconds)...
                set "started="
                REM Use double percent inside Jenkins batch for loops
                for /l %%i in (1,1,12) do (
                    echo Checking Flask (attempt %%i)...
                    timeout /t 5 >nul
                    curl -s http://localhost:%FLASK_PORT% >nul 2>&1 && set started=1 && goto :started
                )

                :started
                if defined started (
                    echo ✅ Flask is running successfully on port %FLASK_PORT%!
                ) else (
                    echo ❌ Flask failed to start after waiting 60 seconds!
                    echo Showing Flask logs below:
                    type flask_log.txt
                    exit /b 1
                )
                '''
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            when {
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                bat '''
                echo === Triggering Airflow DAG ===
                curl -X POST "http://localhost:8080/api/v1/dags/voyage_analytics_dag/dagRuns" ^
                    -H "Content-Type: application/json" ^
                    -u airflow:airflow ^
                    -d "{\\"conf\\":{\\"triggered_by\\":\\"jenkins\\"}}"
                '''
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up Flask process...'
            bat '''
            for /F "tokens=5" %%p in ('netstat -aon ^| findstr :%FLASK_PORT% ^| findstr LISTENING') do (
                echo Killing Flask process PID %%p
                taskkill /F /PID %%p
            )
            '''
        }

        failure {
            echo '❌ Pipeline failed. Showing Flask logs (if any):'
            bat '''
            echo ========= FLASK LOG (ON FAILURE) =========
            if exist flask_log.txt type flask_log.txt
            echo ==========================================
            '''
        }

        success {
            echo '✅ Pipeline completed successfully!'
        }
    }
}
