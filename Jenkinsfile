pipeline {
    agent any

    environment {
        VENV = '.venv\\Scripts\\activate'
        PYTHON = '.venv\\Scripts\\python.exe'
        APP_PATH = 'src\\app.py'
        MODEL_PATH = 'model\\voyage_model\\1\\model.pkl'
        FLASK_LOG = 'flask_log.txt'
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
                    if exist "${MODEL_PATH}" (
                        echo [INFO] Model found at ${MODEL_PATH}
                        ${PYTHON} src/test_model.py
                    ) else (
                        echo [ERROR] Model not found at ${MODEL_PATH}
                        exit /b 1
                    )
                """
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                echo 'Starting Flask app in background...'

                // 🧹 Kill old Flask process (if running)
                bat '''
                    for /f "tokens=5" %%p in ('netstat -aon ^| findstr :5050 ^| findstr LISTENING') do (
                        echo Killing old Flask process with PID %%p
                        taskkill /F /PID %%p
                    )
                '''

                // 🚀 Start Flask app in background
                bat """
                    call ${VENV}
                    echo [INFO] Launching Flask app...
                    start cmd /c "${PYTHON} ${APP_PATH} > ${FLASK_LOG} 2>&1"
                    echo [INFO] Waiting 10 seconds for Flask to start...
                    timeout /t 10 >nul
                """

                // 🧪 Check Flask health
                script {
                    def success = false
                    for (int i = 0; i < 3; i++) {
                        echo "🔁 Checking Flask availability (attempt ${i + 1}/3)..."
                        def result = bat(returnStatus: true, script: 'curl -s http://127.0.0.1:5050')
                        if (result == 0) {
                            echo '✅ Flask app is running at http://127.0.0.1:5050'
                            success = true
                            break
                        }
                        sleep 5
                    }
                    if (!success) {
                        echo '❌ Flask app did not respond after 3 attempts — showing log below.'
                        bat 'if exist flask_log.txt type flask_log.txt'
                        error('Flask did not start properly.')
                    }
                }

                // 🧾 Print logs if everything’s fine
                bat """
                    echo ========= FLASK APP LOG =========
                    if exist ${FLASK_LOG} type ${FLASK_LOG}
                    echo =================================
                """
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            steps {
                echo 'Triggering Airflow DAG via REST API...'
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
            // 🛑 Stop Flask app after success
            bat '''
                for /f "tokens=5" %%p in ('netstat -aon ^| findstr :5050 ^| findstr LISTENING') do (
                    echo Stopping Flask app with PID %%p
                    taskkill /F /PID %%p
                )
            '''
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
            bat '''
                echo ========= FLASK LOG ON FAILURE =========
                if exist flask_log.txt type flask_log.txt
                echo ========================================
            '''
        }
    }
}
