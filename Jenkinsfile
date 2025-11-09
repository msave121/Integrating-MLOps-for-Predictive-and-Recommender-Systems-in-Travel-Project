// pipeline {
//     agent any

//     environment {
//         VENV_DIR  = ".venv"
//         PYTHON    = "${VENV_DIR}\\Scripts\\python.exe"
//         ACTIVATE  = "${VENV_DIR}\\Scripts\\activate"
//         MODEL_PATH = "model\\voyage_model\\1\\model.pkl"
//         APP_PATH   = "src\\app.py"
//     }

//     stages {

//         stage('⚙️ Setup Environment') {
//             steps {
//                 echo "Setting up Python environment..."
//                 bat """
//                     if not exist %VENV_DIR% (
//                         python -m venv %VENV_DIR%
//                     )
//                     call %VENV_DIR%\\Scripts\\activate
//                     pip install --upgrade pip
//                     pip install -r requirements.txt
//                 """
//             }
//         }

//         stage('🏗️ Build Model') {
//             steps {
//                 echo "Training model..."
//                 bat """
//                     call %ACTIVATE%
//                     %PYTHON% src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv
//                 """
//             }
//         }

//         stage('🧠 Test Model') {
//             steps {
//                 echo "Testing model..."
//                 bat """
//                     call %ACTIVATE%
//                     if exist "%MODEL_PATH%" (
//                         echo [INFO] Model found at %MODEL_PATH%
//                         %PYTHON% src/test_model.py
//                     ) else (
//                         echo [ERROR] Model not found at %MODEL_PATH%
//                         exit /b 1
//                     )
//                 """
//             }
//         }

//         stage('🚀 Deploy') {
//             steps {
//                 echo "Deploying Flask app..."
//                 bat """
//                     call %ACTIVATE%
//                     if exist "%APP_PATH%" (
//                         echo [INFO] Starting Flask app in background...

//                         for /f "tokens=2 delims==," %%a in ('wmic process where "CommandLine like '%%src\\\\app.py%%'" get ProcessId /value ^| find "ProcessId="') do taskkill /PID %%a /F >nul 2>&1

//                         start "FLASK-APP" cmd /c "%PYTHON% %APP_PATH% > flask_log.txt 2>&1"

//                         ping -n 6 127.0.0.1 >nul

//                         powershell -NoProfile -Command "try{ iwr -UseBasicParsing http://127.0.0.1:5050 -TimeoutSec 10 | Out-Null; exit 0 } catch { exit 1 }"
//                         if errorlevel 1 (
//                             echo [ERROR] Flask did not start, recent log:
//                             powershell -NoProfile -Command "Get-Content -Tail 50 .\\flask_log.txt"
//                             exit /b 1
//                         )
//                     ) else (
//                         echo [ERROR] app.py not found at %APP_PATH%
//                         exit /b 1
//                     )
//                 """
//                 echo "✅ Flask app started successfully at http://127.0.0.1:5050"
//             }
//         }
//     }

//     post {
//         always {
//             echo 'Cleaning up any background Flask process (if running)...'
//             // Kill the console window started with title FLASK-APP (best-effort)
//             bat 'taskkill /FI "WINDOWTITLE eq FLASK-APP" /F >nul 2>&1'
//         }
//         success {
//             echo '✅ Pipeline completed successfully!'
//         }
//         failure {
//             echo '❌ Pipeline failed. Check logs for details.'
//         }
//     }
// }


pipeline {
    agent any

    environment {
        PYTHON = ".venv\\Scripts\\python.exe"
        PORT = "5055"
        APP_PATH = "src\\app.py"
        POWERSHELL = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        NETSTAT = "C:\\Windows\\System32\\netstat.exe"
        FINDSTR = "C:\\Windows\\System32\\findstr.exe"
        TIMEOUT = "C:\\Windows\\System32\\timeout.exe"
    }

    stages {

        stage('📦 Checkout Code') {
            steps {
                checkout scm
                bat 'echo ✅ Code checked out from GitHub.'
            }
        }

        stage('🐍 Setup Python Environment') {
            steps {
                bat '''
                if not exist .venv (
                    echo Creating virtual environment...
                    python -m venv .venv
                )
                call .venv\\Scripts\\activate
                echo Installing dependencies...
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('🧠 Train & Test Model') {
            steps {
                bat '''
                echo Training model...
                call .venv\\Scripts\\activate
                %PYTHON% src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                echo ✅ Model trained successfully.
                echo Testing model...
                %PYTHON% src\\test_model.py
                echo ✅ Model test complete.
                '''
            }
        }

        stage('🚀 Run Flask API') {
            steps {
                bat '''
                echo === Deploying Flask App on port %PORT% ===

                rem --- Kill any process on port 5055 (ignore errors) ---
                "%NETSTAT%" -aon | "%FINDSTR%" :%PORT% > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
                del temp_netstat.txt >nul 2>&1

                echo Starting Flask app...
                del flask_log.txt >nul 2>&1

                rem --- Run Flask in background safely ---
                start "" "%POWERSHELL%" -NoProfile -ExecutionPolicy Bypass -Command ^
                    "cd '%cd%'; & '%PYTHON%' %APP_PATH% *> flask_log.txt 2>&1 &"

                echo Waiting for Flask to start...
                "%TIMEOUT%" /t 25 /nobreak >nul

                echo Checking Flask health...
                curl -s http://localhost:%PORT%/ >nul 2>&1
                if errorlevel 1 (
                    echo ❌ Flask failed health check!  
                    echo ======= FLASK LOG =======  
                    type flask_log.txt  
                    echo ==========================  
                    exit /b 1 
                ) else (
                    echo ✅ Flask is running successfully on port %PORT%!
                )
                '''
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                bat '''
                echo Triggering Airflow DAG...
                curl -u admin:admin -X POST http://localhost:8080/api/v1/dags/voyage_analytics_dag/dagRuns \
                     -H "Content-Type: application/json" \
                     -d "{\\"conf\\": {\\"triggered_by\\": \\"jenkins\\"}}"
                '''
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up Flask process after pipeline...'
            bat '''
            "%NETSTAT%" -aon | "%FINDSTR%" :%PORT% > temp_netstat.txt 2>nul
            for /F "tokens=5" %%p in (temp_netstat.txt) do (
                echo Stopping Flask process %%p  
                taskkill /F /PID %%p >nul 2>&1
            )
            del temp_netstat.txt >nul 2>&1
            echo ✅ Cleanup complete.
            '''
        }

        failure {
            echo '❌ Pipeline failed. Showing Flask logs below (if any):'
            bat '''
            echo ========= FLASK LOG (ON FAILURE) ========= 
            if exist flask_log.txt type flask_log.txt 
            echo ==========================================
            '''
        }
    }
}
