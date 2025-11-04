pipeline {
    agent any

    stages {

        stage('Clean Workspace') {
            steps {
                bat '''
                echo Cleaning old virtual environment...
                if exist .venv rmdir /s /q .venv
                '''
            }
        }

        stage('Setup Python Virtualenv') {
            steps {
                bat '''
                echo Creating new virtual environment...
                python -m venv .venv
                call .venv\\Scripts\\activate
                python -m pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                echo Installing dependencies from requirements.txt...
                call .venv\\Scripts\\activate
                pip install -r requirements.txt
                '''
            }
        }

        stage('Build Model') {
            steps {
                bat '''
                echo Running training script...
                call .venv\\Scripts\\activate
                python src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv
                '''
            }
        }

        stage('Test Model') {
            steps {
                bat '''
                echo Running test script...
                call .venv\\Scripts\\activate
                python src/test_model.py
                '''
            }
        }

        stage('Deploy') {
            steps {
                bat '''
                echo Simulating deployment...
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline completed successfully."
        }
        failure {
            echo "Pipeline failed. Check logs for details."
        }
    }
}
