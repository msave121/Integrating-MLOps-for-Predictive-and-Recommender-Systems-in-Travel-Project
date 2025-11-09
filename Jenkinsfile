pipeline {
    agent any

    environment {
        VENV = '.venv'
        PYTHON = "${env.WORKSPACE}\\.venv\\Scripts\\python.exe"
    }

    stages {

        stage('Setup Environment') {
            steps {
                bat '''
                echo === Setting up virtual environment ===

                if not exist %VENV% (
                    echo Creating virtual environment...
                    python -m venv %VENV%
                )

                call %VENV%\\Scripts\\activate
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                bat '''
                echo === Training Model ===
                call %VENV%\\Scripts\\activate
                python src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                '''
            }
        }

        stage('Test Model') {
            steps {
                bat '''
                echo === Testing Model ===
                call %VENV%\\Scripts\\activate
                python src\\test_model.py
                '''
            }
        }

        stage('Deploy Flask App') {
            steps {
                bat '''
                echo === Starting Flask App ===
                
                rem --- Kill any process using the port ---
                "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :5055 > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
                del temp_netstat.txt 2>nul

                rem --- Start Flask in background ---
                del flask_log.txt 2>nul
                echo Starting Flask app in background...
                start "" cmd /c "call .venv\\Scripts\\activate && python src\\app.py > flask_log.txt 2>&1"

                rem --- Wait for Flask to start ---
                echo Waiting for Flask to start...
                powershell -Command "Start-Sleep -Seconds 20"

                rem --- Check health endpoint ---
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

        success {
            echo '✅ Pipeline completed successfully!'
        }
    }
}
