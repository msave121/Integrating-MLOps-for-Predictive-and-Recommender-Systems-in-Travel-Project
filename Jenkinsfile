pipeline {
    agent any

    environment {
        VENV_DIR = ".venv"
        PYTHON = "${VENV_DIR}\\Scripts\\python.exe"
        ACTIVATE = "call ${VENV_DIR}\\Scripts\\activate"
        MODEL_PATH = "model\\voyage_model\\1\\model.pkl"
        APP_PATH = "src\\app.py"
        FLASK_LOG = "flask_log.txt"
    }

    stages {

        stage('⚙️ Setup Environment') {
            steps {
                echo "Setting up Python environment..."
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

        stage('🏗️ Build Model') {
            steps {
                echo "Training model..."
                bat """
                    call %ACTIVATE%
                    %PYTHON% src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv
                """
            }
        }

        stage('🧠 Test Model') {
            steps {
                echo "Testing model..."
                bat """
                    call %ACTIVATE%
                    if exist "%MODEL_PATH%" (
                        echo [INFO] Model found at %MODEL_PATH%
                        %PYTHON% src/test_model.py
                    ) else (
                        echo [ERROR] Model not found at %MODEL_PATH%
                        exit /b 1
                    )
                """
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                echo 'Starting Flask app in background...'
                bat """
                    call %ACTIVATE%
                    if exist %FLASK_LOG% del %FLASK_LOG%
                    start cmd /c "%PYTHON% %APP_PATH% > %FLASK_LOG% 2>&1"
                """

                echo '⌛ Waiting for Flask app to start...'
                // Fix: run loop using single-line style so Jenkins doesn’t break
                bat """
                    setlocal enabledelayedexpansion
                    set SUCCESS=0
                    for /L %%i in (1,1,20) do (
                        curl -s http://127.0.0.1:5050 >nul 2>&1
                        if !errorlevel! EQU 0 (
                            echo [✅] Flask app started successfully at http://127.0.0.1:5050
                            set SUCCESS=1
                            goto :done
                        )
                        echo Waiting for Flask to start (%%i/20)...
                        timeout /t 2 >nul
                    )
                    :done
                    if !SUCCESS! EQU 0 (
                        echo [ERROR] Flask did not start in time.
                        type %FLASK_LOG%
                        exit /b 1
                    )
                    endlocal
                """
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
        }
    }
}
