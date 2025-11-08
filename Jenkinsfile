pipeline {
    agent any

    environment {
        VENV_DIR = ".venv"
        PYTHON = "${WORKSPACE}\\${VENV_DIR}\\Scripts\\python.exe"
        PIP = "${WORKSPACE}\\${VENV_DIR}\\Scripts\\pip.exe"
        FLASK_PORT = "5055"
        FLASK_LOG = "flask_log.txt"
    }

    stages {

        stage('🧱 Setup Environment') {
            steps {
                bat '''
                echo === Setting up Python Virtual Environment ===

                if not exist %VENV_DIR% (
                    echo Creating virtual environment...
                    python -m venv %VENV_DIR%
                )

                echo Activating and upgrading pip...
                call %PIP% install --upgrade pip setuptools wheel
                echo ✅ Environment ready.
                '''
            }
        }

        stage('📦 Install Dependencies') {
            steps {
                bat '''
                echo === Installing Dependencies ===
                call %PIP% install -r requirements.txt
                echo ✅ Dependencies installed successfully.
                '''
            }
        }

        stage('🧠 Train Model') {
            steps {
                bat '''
                echo === Training Regression Model ===
                call %PYTHON% src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                if %errorlevel% neq 0 (
                    echo ❌ Model training failed.
                    exit /b 1
                )
                echo ✅ Model trained successfully.
                '''
            }
        }

        stage('🧪 Test Model') {
            steps {
                bat '''
                echo === Testing Regression Model ===
                call %PYTHON% src\\test_model.py
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

                rem Kill existing Flask instances (if any)
                for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%FLASK_PORT%') do taskkill /PID %%a /F >nul 2>&1

                rem Start Flask (logs redirected)
                echo Starting Flask app...
                call %PYTHON% src\\app.py > %FLASK_LOG% 2>&1 &

                echo Waiting 25 seconds for Flask to start...
                timeout /t 25 >nul

                echo --- Flask Log Preview ---
                if exist %FLASK_LOG% (
                    type %FLASK_LOG%
                ) else (
                    echo (no log found)
                )
                echo --- End Preview ---

                echo Checking Flask health on http://localhost:%FLASK_PORT%/ ...
                curl -s http://localhost:%FLASK_PORT%/ >nul
                if %errorlevel% neq 0 (
                    echo ❌ Flask API did not respond on port %FLASK_PORT%.
                    echo ======= FLASK LOG DUMP =======
                    if exist %FLASK_LOG% type %FLASK_LOG%
                    echo ==========================================
                    exit /b 1
                ) else (
                    echo ✅ Flask started successfully on port %FLASK_PORT%.
                )
                '''
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            when {
                expression {
                    // Run this stage only if Flask succeeded
                    currentBuild.resultIsBetterOrEqualTo('SUCCESS')
                }
            }
            steps {
                bat '''
                echo === Triggering Airflow DAG ===
                curl -X POST "http://localhost:8080/api/v1/dags/voyage_analytics_dag/dagRuns" ^
                     -H "Content-Type: application/json" ^
                     -u "airflow:airflow" ^
                     -d "{\\"conf\\": {\\"triggered_by\\": \\"jenkins_pipeline\\"}}"
                if %errorlevel% neq 0 (
                    echo ❌ Airflow trigger failed.
                    exit /b 1
                )
                echo ✅ Airflow DAG triggered successfully.
                '''
            }
        }
    }

    post {
        failure {
            echo '❌ Pipeline failed. Showing Flask logs below (if any):'
            bat '''
            echo ========= FLASK LOG (ON FAILURE) =========
            if exist %FLASK_LOG% type %FLASK_LOG%
            echo ==========================================
            '''
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
    }
}
