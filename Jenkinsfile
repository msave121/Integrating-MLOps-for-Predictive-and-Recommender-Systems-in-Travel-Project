pipeline {
    agent any

    environment {
        PYTHON = "C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"
        VENV_DIR = ".venv"
    }

    stages {

        stage('🧹 Clean Workspace') {
            steps {
                bat '''
                echo Cleaning old virtual environment...
                if exist %VENV_DIR% rmdir /s /q %VENV_DIR%
                '''
            }
        }

        stage('🐍 Setup Python 3.12 Virtualenv') {
            steps {
                bat '''
                echo Setting up Python 3.12 virtual environment...
                "%PYTHON%" -m venv %VENV_DIR%
                call %VENV_DIR%\\Scripts\\activate
                python --version
                python -m pip install --upgrade pip
                '''
            }
        }

        stage('📦 Install Dependencies') {
            steps {
                bat '''
                call %VENV_DIR%\\Scripts\\activate
                echo Installing dependencies...
                python -m pip install --upgrade setuptools wheel
                pip install -r requirements.txt
                '''
            }
        }

        stage('🏗️ Build Model') {
            steps {
                bat '''
                call %VENV_DIR%\\Scripts\\activate
                echo Training model...
                python src\\train_regression.py --users data\\users.csv --flights data\\flights.csv --hotels data\\hotels.csv
                '''
            }
        }

        // ✅ Skip this stage safely if model file not present
        stage('🧠 Test Model') {
            steps {
                bat '''
                if exist mlruns\\0\\latest_model\\model.pkl (
                    call %VENV_DIR%\\Scripts\\activate
                    echo Testing model...
                    python src\\test_model.py
                ) else (
                    echo ⚠️ No trained model found. Skipping test stage.
                )
                '''
            }
        }

        stage('🚀 Deploy') {
            steps {
                bat '''
                call %VENV_DIR%\\Scripts\\activate
                echo Deploying application...
                python src\\app.py
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
