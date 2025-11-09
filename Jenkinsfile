pipeline {
    agent any

    environment {
        FLASK_PORT = "5055"
    }

    stages {

        stage('🧹 Clean Workspace') {
            steps {
                echo "Cleaning up workspace..."
                bat 'del /Q flask_log.txt 2>nul || echo (no existing log)'
            }
        }

        stage('🐍 Setup Python Environment') {
            steps {
                echo "Setting up Python virtual environment..."
                bat '''
                if not exist .venv (
                    echo Creating virtual environment...
                    python -m venv .venv
                )
                .venv\\Scripts\\python.exe -m pip install --upgrade pip
                .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('📊 Train Model') {
            steps {
                echo "=== Training Model ==="
                bat '''
                .venv\\Scripts\\python.exe src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                '''
            }
        }

        stage('🧪 Test Model') {
            steps {
                echo "=== Testing Model ==="
                bat '''
                .venv\\Scripts\\python.exe src\\test_model.py
                '''
            }
        }

        stage('🚀 Run Flask App') {
            steps {
                echo "=== Deploying Flask App on port ${FLASK_PORT} ==="
                bat '''
                rem --- Kill any process using the port (ignore errors) ---
                "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :%FLASK_PORT% > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
                del temp_netstat.txt 2>nul

                rem --- Start Flask app in background ---
                echo Starting Flask app...
                del flask_log.txt 2>nul
                start "" cmd /c ".venv\\Scripts\\python.exe src\\app.py > flask_log.txt 2>&1"

                echo Waiting for Flask to start...
                timeout /t 20 /nobreak >nul

                echo Checking Flask health...
                curl -s http://localhost:%FLASK_PORT% >nul 2>&1
                if errorlevel 1 (
                    echo ❌ Flask failed health check!
                    echo ======= FLASK LOG =======
                    type flask_log.txt
                    echo ==========================
                    exit /b 1
                ) else (
                    echo ✅ Flask is running successfully on port %FLASK_PORT%!
                )
                '''
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Flask process..."
            bat '''
            "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :%FLASK_PORT% > temp_netstat.txt 2>nul
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
