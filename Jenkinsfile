pipeline {
    agent any

    environment {
        PYTHON = '.venv\\Scripts\\python.exe'
        APP_PATH = 'src\\app.py'
        MODEL_PATH = 'model\\voyage_model\\1\\model.pkl'
        FLASK_LOG = 'flask_log.txt'
        FLASK_PORT = '5055'

        AIRFLOW_USER = 'admin'
        AIRFLOW_PASS = 'admin'
        AIRFLOW_DAG_ID = 'reload_model_dag'
        AIRFLOW_URL = 'http://localhost:8080/api/v1/dags/${AIRFLOW_DAG_ID}/dagRuns'
    }

    stages {
        stage('🧹 Clean Workspace') {
            steps {
                echo 'Cleaning workspace...'
                bat 'if exist model rmdir /s /q model'
                bat 'if exist mlruns rmdir /s /q mlruns'
                bat 'if exist flask_log.txt del /q flask_log.txt'
            }
        }

        stage('🐍 Setup Virtual Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                bat """
                    if not exist .venv (
                        python -m venv .venv
                    )
                    ${PYTHON} -m pip install --upgrade pip
                    ${PYTHON} -m pip install -r requirements.txt
                """
            }
        }

        stage('🏗️ Build Model') {
            steps {
                echo 'Training model...'
                bat """
                    ${PYTHON} src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv
                """
            }
        }

        stage('🧠 Test Model') {
            steps {
                echo 'Testing model...'
                bat """
                    ${PYTHON} src/test_model.py
                """
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                echo 'Starting Flask app in background...'
                bat """
                    for /F "tokens=5" %%p in ('netstat -aon ^| findstr :${FLASK_PORT} ^| findstr LISTENING') do (
                        echo Killing old Flask process with PID %%p  
                        taskkill /F /PID %%p
                    )

                    start cmd /c "${PYTHON} ${APP_PATH} > ${FLASK_LOG} 2>&1"
                    timeout /t 8
                """

                // Verify Flask is running
                bat """
                    curl -s http://127.0.0.1:${FLASK_PORT}
                """
                echo "✅ Flask app started successfully at http://127.0.0.1:${FLASK_PORT}"
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
                echo ========= FLASK LOG ON FAILURE =========
                if exist ${FLASK_LOG} type ${FLASK_LOG}
                echo ========================================
            """
        }
    }
}
