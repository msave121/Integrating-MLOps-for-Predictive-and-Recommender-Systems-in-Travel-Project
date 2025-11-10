pipeline {
    agent any

    environment {
        PYTHON = "${WORKSPACE}\\.venv\\Scripts\\python.exe"
        PORT = "5055"
    }

    stages {
        stage('Setup Environment') {
            steps {
                echo "=== Setting up Python virtual environment ==="
                bat '''
                if not exist .venv (
                    python -m venv .venv
                )
                call .venv\\Scripts\\activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                echo "=== Training Model ==="
                bat '''
                call .venv\\Scripts\\activate
                python src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                '''
            }
        }

        stage('Deploy Flask App') {
            steps {
                echo "=== Starting Flask App ==="
                bat '''
                rem --- Kill any process using the port ---
                "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :%PORT% > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
                del temp_netstat.txt 2>nul

                rem --- Start Flask in background ---
                del flask_log.txt 2>nul
                echo Starting Flask app in background...
                start "" cmd /c "call .venv\\Scripts\\activate && python src\\app.py > flask_log.txt 2>&1"

                rem --- Wait 15 seconds for Flask to boot ---
                powershell -Command "Start-Sleep -Seconds 15"

                rem --- Health check ---
                echo Checking Flask health...
                curl -s http://localhost:%PORT% >nul 2>&1
                if errorlevel 1 (
                    echo ❌ Flask failed health check!
                    echo ======= FLASK LOG =======
                    if exist flask_log.txt type flask_log.txt
                    echo ==========================
                    exit /b 1
                ) else (
                    echo ✅ Flask is running successfully on port %PORT%!
                )
                '''
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Flask process..."
            bat '''
            "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :%PORT% > temp_netstat.txt 2>nul
            for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
            del temp_netstat.txt 2>nul
            echo ✅ Cleanup complete.
            '''
        }
        failure {
            echo "❌ Pipeline failed. Showing Flask logs below (if any):"
            bat '''
            echo ========= FLASK LOG (ON FAILURE) =========
            if exist flask_log.txt type flask_log.txt
            echo ==========================================
            '''
        }
    }
}
