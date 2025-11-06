pipeline {
    agent any

    environment {
        PYTHON = 'python'
        VENV = '.venv\\Scripts\\activate'
    }

    stages {
        stage('🧹 Clean Workspace') {
            steps {
                echo 'Cleaning workspace...'
                bat 'if exist model rmdir /s /q model'
                bat 'if exist mlruns rmdir /s /q mlruns'
            }
        }

        stage('🐍 Setup Virtual Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                bat """
                    if not exist .venv (
                        python -m venv .venv
                    )
                    call ${VENV}
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('🏗️ Build Model') {
            steps {
                echo 'Training model...'
                bat """
                    call ${VENV}
                    python src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv
                """
            }
        }

        stage('🧠 Test Model') {
            steps {
                echo 'Testing model...'
                bat """
                    call ${VENV}
                    python src/test_model.py
                """
            }
        }

        stage('🚀 Deploy') {
            steps {
                echo 'Deploying Flask application in background...'
                bat """
                    call ${VENV}
                    echo Starting Flask app on port 5050...
                    start /B cmd /c "python src/app.py > flask_log.txt 2>&1"
                """
                echo '✅ Flask app started successfully (logs -> flask_log.txt)'
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo 'You can access your Flask app at: http://127.0.0.1:5050'
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
        }
    }
}
