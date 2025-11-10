pipeline {
    agent any

    environment {
        PYTHON = '.venv\\Scripts\\python.exe'
        PIP = '.venv\\Scripts\\pip.exe'
    }

    stages {
        stage('Setup Environment') {
            steps {
                echo '=== Setting up virtual environment ==='
                bat '''
                if not exist .venv (
                    echo Creating virtual environment...
                    python -m venv .venv
                )
                call .venv\\Scripts\\activate
                %PIP% install --upgrade pip
                %PIP% install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                echo '=== Training Model ==='
                bat '''
                call .venv\\Scripts\\activate && %PYTHON% src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                '''
            }
        }

        stage('Deploy Flask App') {
            steps {
                echo '=== Starting Flask App ==='
                bat '''
                rem --- Kill any process using the port ---
                "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :5055 > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
                del temp_netstat.txt 2>nul

                rem --- Start Flask in background ---
                del flask_log.txt 2>nul
                echo Starting Flask app in background...
                start "" cmd /c "call .venv\\Scripts\\activate && python src\\app.py > flask_log.txt 2>&1"

                rem --- Wait for Flask to start (20 sec loop) ---
                echo Waiting for Flask to start...
                for /L %%i in (1,1,20) do (
                    ping 127.0.0.1 -n 2 >nul
                )

                rem --- Health check ---
                echo Checking Flask health...
                curl -s http://localhost:5055 >nul 2>&1

                if errorlevel 1 (
                    echo ❌ Flask failed health check!  
                    echo ======= FLASK LOG =======  
                    if exist flask_log.txt type flask_log.txt  
                    echo ==========================  
                    exit /b 1 
                ) else (
                    echo ✅ Flask is running successfully on port 5055!
                )
                '''
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up Flask process...'
            bat '''
            "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :5055 > temp_netstat.txt 2>nul
            for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
            del temp_netstat.txt 2>nul
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
