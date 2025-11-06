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
                echo 'Deploying application...'
                // Run Flask in background using "start /B"
                bat """
                    call ${VENV}
                    echo Starting Flask app in background...
                    start /B python src/app.py
                """
                echo '✅ Flask app started successfully in background.'
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
        }
    }
}
