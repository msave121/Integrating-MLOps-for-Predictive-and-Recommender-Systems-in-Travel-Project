pipeline {
    agent any

    stages {

        stage('🧹 Clean Workspace') {
            steps {
                bat '''
                if exist .venv rmdir /s /q .venv
                '''
            }
        }

        stage('🐍 Setup Python Virtualenv') {
            steps {
                bat '''
                python -m venv .venv
                call .venv\\Scripts\\activate
                python -m pip install --upgrade pip
                '''
            }
        }

        stage('📦 Install Dependencies') {
            steps {
                bat '''
                call .venv\\Scripts\\activate
                echo Installing requirements (binary-only)...
                pip install --only-binary=:all: -r requirements.txt
                '''
            }
        }

        stage('🏗️ Build Model') {
            steps {
                bat '''
                call .venv\\Scripts\\activate
                python src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv
                '''
            }
        }

        stage('🧠 Test Model') {
            steps {
                bat '''
                call .venv\\Scripts\\activate
                python src/test_model.py
                '''
            }
        }

        stage('🚀 Deploy') {
            steps {
                bat '''
                echo Simulating deployment...
                '''
            }
        }
    }

    post {
        always {
            echo "✅ Pipeline completed"
        }
        failure {
            echo "❌ Pipeline failed. Check logs for details."
        }
    }
}
