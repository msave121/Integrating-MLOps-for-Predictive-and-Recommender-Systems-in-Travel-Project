pipeline {
    agent any

    stages {

        stage('🧹 Clean Workspace') {
            steps {
                bat '''
                echo Cleaning old virtual environment...
                if exist .venv rmdir /s /q .venv
                '''
            }
        }

        stage('🐍 Setup Python 3.12 Virtualenv') {
            steps {
                bat '''
                echo Setting up Python 3.12 virtual environment...
                "C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m venv .venv
                call .venv\\Scripts\\activate
                python -m pip install --upgrade pip
                '''
            }
        }

        stage('📦 Install Dependencies') {
            steps {
                bat '''
                call .venv\\Scripts\\activate
                echo Installing dependencies...
                pip install -r requirements.txt
                '''
            }
        }

        stage('🏗️ Build Model') {
            steps {
                bat '''
                call .venv\\Scripts\\activate
                echo Training model...
                python src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                '''
            }
        }

        stage('🧠 Test Model') {
            steps {
                bat '''
                call .venv\\Scripts\\activate
                echo Testing model...
                python src\\test_model.py
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
