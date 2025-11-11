pipeline {
    agent any

    environment {
        VENV_DIR   = '.venv'
        PYTHON     = '.venv\\Scripts\\python.exe'
        ACTIVATE   = 'call .venv\\Scripts\\activate'
        MODEL_PATH = 'model\\voyage_model\\1\\model.pkl'
        APP_PATH   = 'src\\app.py'
        FLASK_PORT = '5055'
        FLASK_URL  = 'http://127.0.0.1:%FLASK_PORT%/health'
    }

    stages {

        stage('⚙️ Setup Environment') {
            steps {
                echo 'Setting up Python environment...'
                bat '''
                if not exist %VENV_DIR% (
                    python -m venv %VENV_DIR%
                )
                call %VENV_DIR%\\Scripts\\activate
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('🏗️ Build Model') {
            steps {
                echo 'Training model...'
                bat '''
                %ACTIVATE%
                %PYTHON% src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                '''
            }
        }

        stage('🧠 Test Model') {
            steps {
                echo 'Testing model...'
                bat '''
                %ACTIVATE%
                if exist "%MODEL_PATH%" (
                    echo [INFO] Model found at %MODEL_PATH%
                    %PYTHON% src\\test_model.py
                ) else (
                    echo [ERROR] Model not found at %MODEL_PATH%
                    exit /b 1
                )
                '''
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                echo 'Deploying Flask app...'
                bat '''
                echo === Starting Flask App ===
                del flask_out.txt 2>nul
                del flask_err.txt 2>nul
                del flask.pid     2>nul

                echo Launching Flask on port %FLASK_PORT%...

                REM Start the app with venv Python, capture PID and split logs
                powershell -NoProfile -Command "$p = Start-Process -FilePath '%PYTHON%' -ArgumentList 'src\\app.py','--host','127.0.0.1','--port','%FLASK_PORT%' -PassThru -WindowStyle Hidden -RedirectStandardOutput 'flask_out.txt' -RedirectStandardError 'flask_err.txt'; $p.Id | Out-File -FilePath 'flask.pid' -Encoding ascii"

                echo Waiting for Flask to fully start (up to 60 seconds)...
                powershell -NoProfile -Command "$deadline=(Get-Date).AddSeconds(60); while((Get-Date)-lt $deadline){ try{ $r=Invoke-WebRequest -UseBasicParsing '%FLASK_URL%' -TimeoutSec 2; if($r.StatusCode -eq 200){ Write-Host 'Flask is up!'; exit 0 } }catch{} Start-Sleep -Seconds 1 }; Write-Error 'Flask did not start in time'; exit 1"
                '''
                echo '✅ Flask app started successfully.'
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up Flask process...'
            bat '''
            REM Prefer killing by PID we saved; fall back to port search
            if exist flask.pid (
                set /p PID=<flask.pid
                if not "%PID%"=="" (
                    echo Killing Flask process PID %PID%
                    powershell -NoProfile -Command "try { Stop-Process -Id %PID% -Force -ErrorAction Stop } catch {}"
                )
                del flask.pid
            ) else (
                echo No PID file found; trying by port %FLASK_PORT%...
                for /F "tokens=5" %%p in ('netstat -aon ^| findstr /r /c:":%FLASK_PORT% .*LISTENING" 2^>nul') do (
                    echo Killing Flask process PID %%p
                    taskkill /F /PID %%p 2>nul
                )
            )
            exit /b 0
            '''
        }

        failure {
            echo '❌ Pipeline failed. Showing Flask logs (if any):'
            bat '''
            echo ========= FLASK LOGS (ON FAILURE) =========
            if exist flask_out.txt (echo --- STDOUT --- & type flask_out.txt)
            if exist flask_err.txt (echo --- STDERR --- & type flask_err.txt)
            echo ==========================================
            '''
        }

        success {
            echo '✅ Pipeline completed successfully!'
        }
    }
}
