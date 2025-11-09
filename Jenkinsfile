pipeline {
    agent any

    environment {
        FLASK_PORT = "5055"
        VENV_PATH = ".venv\\Scripts\\python.exe"
        FLASK_APP = "src\\app.py"
    }

    stages {
        stage('🧹 Clean Workspace') {
            steps {
                echo "Cleaning old files..."
                bat '''
                del /F /Q flask_log.txt 2>nul
                del /F /Q temp_netstat.txt 2>nul
                '''
            }
        }

        stage('🐍 Setup Virtual Environment') {
            steps {
                echo "Activating virtual environment..."
                bat '''
                if not exist .venv (
                    echo ❌ Virtual environment not found! Please set it up before running Jenkins.
                    exit /b 1
                )
                .venv\\Scripts\\pip install -r requirements.txt
                '''
            }
        }

        stage('🚀 Run Flask App') {
            steps {
                echo "=== Deploying Flask App on port ${FLASK_PORT} ==="
                bat '''
                rem --- Kill any old Flask process using the port ---
                "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :%FLASK_PORT% > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
                del temp_netstat.txt 2>nul

                rem --- Start Flask in background ---
                echo Starting Flask app...
                del flask_log.txt 2>nul
                start "" cmd /c "%VENV_PATH% %FLASK_APP% > flask_log.txt 2>&1"

                echo Waiting for Flask to start...
                ping 127.0.0.1 -n 15 >nul

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
