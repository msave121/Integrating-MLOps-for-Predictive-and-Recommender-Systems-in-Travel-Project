pipeline {
    agent any

    environment {
        VENV = '.venv\\Scripts\\activate'
        PYTHON = '.venv\\Scripts\\python.exe'
        APP_PATH = 'src\\app.py'
        MODEL_PATH = 'model\\voyage_model\\1\\model.pkl'
        FLASK_LOG = 'flask_log.txt'
        AIRFLOW_USER = 'manasvi'
        AIRFLOW_PASS = 'Save@123'
        AIRFLOW_DAG_ID = 'reload_model_dag'
        AIRFLOW_URL = 'http://localhost:8080/api/v1/dags/${AIRFLOW_DAG_ID}/dagRuns'
    }

    stages {

        stage('🧹 Clean Workspace') {
            steps {
                echo 'Cleaning workspace...'
                bat 'if exist model rmdir /s /q model'
                bat 'if exist mlruns rmdir /s /q mlruns'
                bat 'if exist flask_log.txt del flask_log.txt'
            }
        }

        stage('🐍 Setup Virtual Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                bat """
                    if not exist .venv (
                        python -m venv .venv
                    )
                    call ${VENV}
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('🏗️ Build Model') {
            steps {
                echo 'Training model...'
                bat """
                    call ${VENV}
                    ${PYTHON} src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv
                """
            }
        }

        stage('🧠 Test Model') {
            steps {
                echo 'Testing model...'
                bat """
                    call ${VENV}
                    ${PYTHON} src/test_model.py
                """
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                echo 'Starting Flask app in background...'

                // 🧹 Kill any existing Flask process to avoid duplicates
                bat """
                    for /f "tokens=5" %%p in ('netstat -aon ^| findstr :5050 ^| findstr LISTENING') do taskkill /F /PID %%p
                """

                // 🚀 Start Flask safely (no redirection issue)
                bat """
                    call ${VENV}
                    start cmd /k "${PYTHON} ${APP_PATH} > ${FLASK_LOG} 2>&1"
                    echo Waiting for Flask to start...
                    timeout /t 10 >nul
                """

                // ✅ Check Flask health
                script {
                    def success = false
                    for (int i = 0; i < 3; i++) {
                        echo "🔁 Checking Flask availability (attempt ${i + 1}/3)..."
                        def result = bat(returnStatus: true, script: 'curl -s http://127.0.0.1:5050')
                        if (result == 0) {
                            echo '✅ Flask app is responding at http://127.0.0.1:5050'
                            success = true
                            break
                        }
                        sleep 5
                    }
                    if (!success) {
                        error('❌ Flask app did not start after 3 attempts.')
                    }
                }

                // 🧾 Print Flask logs to Jenkins console
                bat """
                    echo ========= FLASK APP LOG =========
                    if exist ${FLASK_LOG} type ${FLASK_LOG}
                    echo =================================
                """
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            steps {
                echo 'Triggering Airflow DAG...'
                bat """
                    curl -u ${AIRFLOW_USER}:${AIRFLOW_PASS} ^
                        -X POST "${AIRFLOW_URL}" ^
                        -H "Content-Type: application/json" ^
                        -d "{\\"conf\\": {\\"triggered_by\\": \\"jenkins\\"}}"
                """
                echo '✅ Airflow DAG triggered successfully.'
            }
        }
    }

    post {
        success {
            echo '✅ CI/CD Pipeline completed successfully — Model trained, tested, deployed, and DAG triggered!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
            bat """
                if exist ${FLASK_LOG} (
                    echo ========= FLASK LOG (ON FAILURE) =========
                    type ${FLASK_LOG}
                    echo ==========================================
                )
            """
        }
    }
}
