pipeline {
    agent any

    environment {
        PYTHON = "C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"
        PYTHONUTF8 = "1"   // fix UnicodeEncodeError on Windows console
    }

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
                "%PYTHON%" -m venv .venv
                call .venv\\Scripts\\activate
                python -m pip install --upgrade pip setuptools wheel
                '''
            }
        }

        stage('📦 Install Dependencies') {
            steps {
                bat '''
                echo Installing dependencies safely...
                call .venv\\Scripts\\activate
                rem install prebuilt core packages first
                pip install numpy==1.26.4 pandas==2.2.2 scikit-learn==1.4.2
                rem now install all remaining deps
                pip install -r requirements.txt --only-binary=:all:
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
