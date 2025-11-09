pipeline {
    agent any

    environment {
        PYTHON                = '.venv\\Scripts\\python.exe'
        VENV_ACTIVATE         = '.venv\\Scripts\\activate'
        FLASK_HOST            = '0.0.0.0'
        FLASK_PORT            = '5055'
        FLASK_LOG             = 'flask_log.txt'

        AIRFLOW_USER          = 'admin'
        AIRFLOW_PWD           = 'admin'
        AIRFLOW_DAG_ID        = 'voyage_analytics_dag'
        AIRFLOW_TRIGGER_URL   = 'http://localhost:8081/api/v1/dags/voyage_analytics_dag/dagRuns'
    }

    stages {

        stage('📦 Setup Environment') {
            steps {
                echo "Setting up virtual environment..."
                bat """
                if not exist .venv (
                    python -m venv .venv
                )
                call %VENV_ACTIVATE%
                %PYTHON% -m pip install --upgrade pip
                %PYTHON% -m pip install -r requirements.txt
                """
            }
        }

        stage('🚀 Run Flask API') {
            steps {
                echo "Starting Flask app on http://%FLASK_HOST%:%FLASK_PORT% ..."
                bat """
                call %VENV_ACTIVATE%

                rem ---- Kill anything already on the port ----
                %SystemRoot%\\System32\\netstat.exe -aon | %SystemRoot%\\System32\\findstr.exe :%FLASK_PORT% > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
                del temp_netstat.txt >nul 2>&1

                rem ---- Start Flask in background and log output ----
                del %FLASK_LOG% >nul 2>&1
                echo Starting Flask...
                start "Flask" /B cmd /c "call %VENV_ACTIVATE% && %PYTHON% src\\app.py --host %FLASK_HOST% --port %FLASK_PORT% > %FLASK_LOG% 2>&1"

                rem ---- Wait up to 30s for /health to respond ----
                set /a _wait=0
                :waitloop
                set /a _wait+=1
                curl -s http://localhost:%FLASK_PORT%/health >nul 2>&1 && goto :ready
                if %_wait% GEQ 30 goto :fail
                timeout /t 1 >nul
                goto :waitloop

                :fail
                echo ❌ Flask failed health check on :%FLASK_PORT% !
                echo ======= FLASK LOG =======
                if exist %FLASK_LOG% type %FLASK_LOG%
                echo =========================
                exit /b 1

                :ready
                echo ✅ Flask is running at http://localhost:%FLASK_PORT%
                echo ---- Last lines from %FLASK_LOG% ----
                if exist %FLASK_LOG% type %FLASK_LOG%
                """
            }
        }

        stage('🌬️ Trigger Airflow DAG') {
            steps {
                echo "Triggering Airflow DAG..."
                bat """
                curl -s -u %AIRFLOW_USER%:%AIRFLOW_PWD% ^
                  -H "Content-Type: application/json" ^
                  -X POST ^
                  %AIRFLOW_TRIGGER_URL% ^
                  -d "{\\"conf\\": {\\"triggered_by\\": \\"Jenkins Pipeline\\"}}" > airflow_trigger_resp.json

                type airflow_trigger_resp.json
                """
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Flask process after pipeline..."
            bat """
            %SystemRoot%\\System32\\netstat.exe -aon | %SystemRoot%\\System32\\findstr.exe :%FLASK_PORT% > temp_netstat.txt 2>nul
            for /F "tokens=5" %%p in (temp_netstat.txt) do (
                echo Stopping Flask process %%p
                taskkill /F /PID %%p >nul 2>&1
            )
            del temp_netstat.txt >nul 2>&1
            echo ✅ Cleanup complete.
            """

            echo "📜 Flask logs (if present):"
            bat """
            echo ========= FLASK LOG =========
            if exist %FLASK_LOG% type %FLASK_LOG%
            echo =============================
            """
        }
    }
}
