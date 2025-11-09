pipeline {
    agent any

    environment {
        VENV_DIR  = ".venv"
        PYTHON    = "${VENV_DIR}\\Scripts\\python.exe"
        ACTIVATE  = "${VENV_DIR}\\Scripts\\activate"   // fixed: no leading "call"
        MODEL_PATH = "model\\voyage_model\\1\\model.pkl"
        APP_PATH   = "src\\app.py"
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

        stage('🚀 Deploy') {
            steps {
                echo "Deploying Flask app..."
                bat """
                    call %ACTIVATE%
                    if exist "%APP_PATH%" (
                        echo [INFO] Starting Flask app in background...

                        REM Best-effort kill any prior process running app.py (optional safety)
                        for /f "tokens=2 delims==," %%a in ('wmic process where "CommandLine like '%%src\\\\app.py%%'" get ProcessId /value ^| find "ProcessId="') do taskkill /PID %%a /F >nul 2>&1

                        REM Start the app with the venv's python
                        start "FLASK-APP" cmd /c "%PYTHON% %APP_PATH% > flask_log.txt 2>&1"

                        REM Wait ~5 seconds (Windows-safe sleep)
                        ping -n 6 127.0.0.1 >nul

                        REM Health check without curl (PowerShell)
                        powershell -NoProfile -Command "try{ iwr -UseBasicParsing http://127.0.0.1:5050 -TimeoutSec 10 | Out-Null; exit 0 } catch { exit 1 }"
                        if errorlevel 1 (
                            echo [ERROR] Flask did not start, recent log:
                            powershell -NoProfile -Command "Get-Content -Tail 50 .\\flask_log.txt"
                            exit /b 1
                        )
                    ) else (
                        echo [ERROR] app.py not found at %APP_PATH%
                        exit /b 1
                    )
                """
                echo "✅ Flask app started successfully at http://127.0.0.1:5050"
            }
        }
    }

    post {
        always {
            echo 'Cleaning up any background Flask process (if running)...'
            REM Kill the console window started with title FLASK-APP (best-effort)
            bat 'taskkill /FI "WINDOWTITLE eq FLASK-APP" /F >nul 2>&1'
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
        }
    }
}
