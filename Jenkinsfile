pipeline {
    agent any

    environment {
        FLASK_PORT = '5055'
        VENV_PATH  = '.venv\\Scripts\\activate'
        FLASK_URL  = "http://127.0.0.1:%FLASK_PORT%/health"
    }

    stages {

        stage('🧰 Setup Python Env') {
            steps {
                bat '''
                echo === Setting up virtual environment ===
                if not exist .venv (
                    echo Creating venv...
                    python -m venv .venv
                )
                call %VENV_PATH%
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('🧪 Run Tests') {
            steps {
                bat '''
                echo === Running tests ===
                call %VENV_PATH%
                pytest -v || exit /b 1
                '''
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                bat '''
                echo === Starting Flask App ===
                del flask_log.txt 2>nul
                del flask.pid 2>nul

                echo Launching Flask on port %FLASK_PORT%...

                REM Start Flask detached and capture its PID in flask.pid
                powershell -NoProfile -Command "$env:VENV_ACTIVATOR = '.venv\\Scripts\\activate'; $cmd = 'cmd /c \"call ' + $env:VENV_ACTIVATOR + ' && python src\\app.py\"'; $p = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cmd -PassThru -WindowStyle Hidden -RedirectStandardOutput 'flask_log.txt' -RedirectStandardError 'flask_log.txt'; $p.Id | Out-File -FilePath 'flask.pid' -Encoding ascii"

                echo Waiting for Flask to fully start (up to 60 seconds)...
                powershell -NoProfile -Command "$deadline=(Get-Date).AddSeconds(60); while((Get-Date)-lt $deadline){ try{ $r=Invoke-WebRequest -UseBasicParsing '%FLASK_URL%' -TimeoutSec 2; if($r.StatusCode -eq 200){ Write-Host 'Flask is up!'; exit 0 } }catch{} Start-Sleep -Seconds 1 }; Write-Error 'Flask did not start in time'; exit 1"
                '''
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            when {
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                bat '''
                echo === Triggering Airflow DAG ===
                curl -X POST "http://localhost:8080/api/v1/dags/voyage_analytics_dag/dagRuns" ^
                    -H "Content-Type: application/json" ^
                    -u airflow:airflow ^
                    -d "{\\"conf\\":{\\"triggered_by\\":\\"jenkins\\"}}"
                '''
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
            echo ========= FLASK LOG (ON FAILURE) =========
            if exist flask_log.txt type flask_log.txt
            echo ==========================================
            '''
        }

        success {
            echo '✅ Pipeline completed successfully!'
        }
    }
}
