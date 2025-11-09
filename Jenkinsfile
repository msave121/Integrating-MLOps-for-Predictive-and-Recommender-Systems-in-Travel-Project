pipeline {
    agent any

    environment {
        PYTHON = '.venv\\Scripts\\python.exe'
    }

    stages {

        stage('🧹 Clean Workspace') {
            steps {
                bat '''
                echo === Cleaning old files and logs ===
                del /F /Q flask_log.txt 2>nul
                del /F /Q temp_netstat.txt 2>nul
                '''
            }
        }

        stage('📦 Setup Python Environment') {
            steps {
                bat '''
                echo === Setting up Python virtual environment ===

                if not exist .venv (
                    echo Creating virtual environment...
                    python -m venv .venv
                ) else (
                    echo Using existing virtual environment...
                )

                echo Installing dependencies...
                call .venv\\Scripts\\activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('🧠 Train Model') {
            steps {
                bat '''
                echo === Training Model ===
                call .venv\\Scripts\\activate
                python src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                '''
            }
        }

        stage('🧪 Test Model') {
            steps {
                bat '''
                echo === Testing Model ===
                call .venv\\Scripts\\activate
                python src\\test_model.py
                '''
            }
        }

        stage('🚀 Deploy Flask App') {
            steps {
                bat '''
                echo === Deploying Flask App on port 5055 ===

                rem --- Kill any old Flask process using the port ---
                "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :5055  > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do (
                    echo Killing process on port 5055 (PID %%p)
                    taskkill /F /PID %%p  >nul 2>&1
                )
                del temp_netstat.txt  2>nul

                rem --- Start Flask in background ---
                echo Starting Flask app...
                del flask_log.txt  2>nul
                start "" cmd /c ".venv\\Scripts\\python.exe src\\app.py > flask_log.txt 2>&1"

                rem --- Wait for Flask to start ---
                echo Waiting for Flask to start...
                "C:\\Windows\\System32\\timeout.exe" /t 15 /nobreak >nul

                rem --- Check Flask health ---
                echo Checking Flask health...
                "C:\\Windows\\System32\\curl.exe" -s http://localhost:5055 >nul 2>&1

                if errorlevel 1 (
                    echo ❌ Flask failed health check!
                    echo ======= FLASK LOG =======
                    type flask_log.txt
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
            echo '🧹 Cleaning up Flask process after pipeline...'
            bat '''
            "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :5055  > temp_netstat.txt 2>nul
            for /F "tokens=5" %%p in (temp_netstat.txt) do (
                echo Stopping Flask process %%p
                taskkill /F /PID %%p  >nul 2>&1
            )
            del temp_netstat.txt  2>nul
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
