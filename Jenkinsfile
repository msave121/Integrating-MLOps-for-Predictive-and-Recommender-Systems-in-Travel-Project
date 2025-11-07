pipeline {
    agent any

    environment {
        VENV_DIR      = '.venv'
        FLASK_PORT    = '5055'
        AIRFLOW_DAG_ID = 'reload_model_dag'
        AIRFLOW_URL   = 'http://localhost:8080'
        AIRFLOW_USER  = 'admin'
        AIRFLOW_PASS  = 'admin'
    }

    stages {

        stage('📦 Setup Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                bat """
                    if not exist %VENV_DIR% (
                        python -m venv %VENV_DIR%
                    )
                    call %VENV_DIR%\\Scripts\\activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('🧠 Train Model') {
            steps {
                echo 'Training regression model...'
                bat """
                    call %VENV_DIR%\\Scripts\\activate
                    python src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv
                """
            }
        }

        stage('🧪 Test Model') {
            steps {
                echo 'Testing model...'
                bat """
                    call %VENV_DIR%\\Scripts\\activate
                    python src/test_model.py
                """
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                echo 'Starting Flask app in background...'
                
                // Kill any old process on Flask port
                bat """
                    for /F "tokens=5" %%p in ('netstat -aon ^| findstr :%FLASK_PORT% ^| findstr LISTENING') do (
                        echo Killing old Flask process with PID %%p
                        taskkill /F /PID %%p
                    )
                """

                // Start Flask in background safely using PowerShell
                powershell """
                    Start-Process -NoNewWindow -FilePath ".venv\\Scripts\\python.exe" -ArgumentList "src/app.py"
                    Start-Sleep -Seconds 10
                """

                // Verify Flask is running
                bat "curl -s http://127.0.0.1:%FLASK_PORT%"
                echo "✅ Flask app started successfully at http://127.0.0.1:%FLASK_PORT%"
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            steps {
                echo 'Triggering Airflow DAG reload_model_dag...'
                powershell """
                    $pair = "%AIRFLOW_USER%:%AIRFLOW_PASS%"
                    $encoded = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
                    Invoke-WebRequest `
                        -Uri "%AIRFLOW_URL%/api/v1/dags/%AIRFLOW_DAG_ID%/dagRuns" `
                        -Method POST `
                        -Headers @{ "Authorization" = "Basic $encoded"; "Content-Type" = "application/json" } `
                        -Body '{ "conf": { "triggered_by": "jenkins" } }'
                """
                echo '✅ Airflow DAG triggered successfully!'
            }
        }
    }

    post {
        success {
            echo "🎉 Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed. Check logs for details."
            bat """
                echo ========= FLASK LOG (ON FAILURE) =========
                if exist flask_log.txt type flask_log.txt
                echo ==========================================
            """
        }
    }
}
