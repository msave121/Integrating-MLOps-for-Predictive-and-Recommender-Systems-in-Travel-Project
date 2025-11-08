stage('🚀 Deploy Flask App') {
    steps {
        bat '''
        echo Starting Flask app...
        for /F "tokens=5" %p in ('netstat -aon ^| findstr :5055 ^| findstr LISTENING') do (
            echo Killing old Flask process with PID %p
            taskkill /F /PID %p
        )

        echo Starting new Flask process...
        start "" cmd /c ".venv\\Scripts\\python.exe src\\app.py > flask_log.txt 2>&1"
        timeout /t 10 >nul

        echo Checking if Flask started...
        type flask_log.txt
        '''
    }
}
