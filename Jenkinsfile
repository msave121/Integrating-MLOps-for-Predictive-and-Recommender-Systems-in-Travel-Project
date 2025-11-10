pipeline {
    agent any

    stages {
        stage('Setup Environment') {
            steps {
                echo '=== Setting up Python Environment ==='
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
                echo '=== Training Model ==='
                bat '''
                call .venv\\Scripts\\activate
                python src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                '''
            }
        }

        stage('Deploy Flask App') {
            steps {
                echo '=== Starting Flask App ==='
                bat '''
                rem --- Kill any process using the port 5055 ---
                "C:\\Windows\\System32\\netstat.exe" -aon | "C:\\Windows\\System32\\findstr.exe" :5055 > temp_netstat.txt 2>nul
                for /F "tokens=5" %%p in (temp_netstat.txt) do taskkill /F /PID %%p >nul 2>&1
                del temp_netstat.txt 2>nul

                rem --- Start Flask app in background ---
                del flask_log.txt 2>nul
                echo Starting Flask app in background...
                start "" cmd /c "call .venv\\Scripts\\activate && python src\\app.py > flask_log.txt 2>&1"

                rem --- Wait for Flask to be ready (up to 60 seconds) ---
                echo Waiting for Flask to report readiness...
                set ready=

                for /L %%i in (1 1 60) do (
                    findstr /C:"Voyage Analytics API is running" flask_log.txt >nul 2>&1 && set ready=1 && goto ready
                    ping 127.0.0.1 -n 2 >nul
                )

                :ready
                if not defined ready (
                    echo ❌ Flask failed to start within 60 seconds!
                    echo ======= FLASK LOG =======
                    type flask_log.txt
                    echo ==========================
                    exit /b 1
                )

                echo ✅ Flask app started successfully!
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

            echo '❌ Pipeline failed. Showing Flask logs below (if any):'
            bat '''
            echo ========= FLASK LOG (ON FAILURE) =========
            if exist flask_log.txt type flask_log.txt
            echo ==========================================
            '''
        }
    }
}
