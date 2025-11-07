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
        AIRFLOW_URL = "http://localhost:8080/api/v1/dags/reload_model_dag/dagRuns"
    }

    stages {

        stage('🧹 Clean Workspace') {
            steps {
                echo 'Cleaning workspace...'
                bat 'if exist model rmdir /s /q model'
                bat 'if exist mlruns rmdir /s /q mlruns'
                bat 'if exist flask_log.txt del /f /q flask_log.txt'
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
                bat """
                    call ${VENV}
                    start cmd /c "${PYTHON} ${APP_PATH} > ${FLASK_LOG} 2>&1"
                    echo Waiting for Flask to start...
                    timeout /t 10 >nul
                """

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

                echo '📜 Showing last lines of Flask log:'
                bat 'type flask_log.txt'
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
            echo '✅ CI/CD Pipeline completed successfully — Model trained, tested, deployed, and Airflow DAG triggered!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
            bat 'if exist flask_log.txt type flask_log.txt'
        }
    }
}
