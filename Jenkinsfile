pipeline {
    agent any

    environment {
        VENV_DIR = ".venv"
        PYTHON = "${VENV_DIR}\\Scripts\\python.exe"
        ACTIVATE = "call ${VENV_DIR}\\Scripts\\activate"
        MODEL_PATH = "model\\voyage_model\\1\\model.pkl"
        APP_PATH = "src\\app.py"
    }

    stages {

        stage('⚙️ Setup Environment') {
            steps {
                echo "Setting up Python environment..."
                bat """
                    if not exist %VENV_DIR% (
                        python -m venv %VENV_DIR%
                    )
                    call %VENV_DIR%\\Scripts\\activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('🏗️ Build Model') {
            steps {
                echo "Training model..."
                bat """
                    call %ACTIVATE%
                    %PYTHON% src/train_regression.py --users data/users.csv --flights data/flights.csv --hotels data/hotels.csv
                """
            }
        }

        stage('🧠 Test Model') {
            steps {
                echo "Testing model..."
                bat """
                    call %ACTIVATE%
                    if exist "%MODEL_PATH%" (
                        echo [INFO] Model found at %MODEL_PATH%
                        %PYTHON% src/test_model.py
                    ) else (
                        echo [ERROR] Model not found at %MODEL_PATH%
                        exit /b 1
                    )
                """
            }
        }

        stage('🚀 Deploy') {
            steps {
                echo "Deploying application..."
                bat """
                    call %ACTIVATE%
                    if exist "%APP_PATH%" (
                        echo [INFO] Starting Flask app...
                        %PYTHON% %APP_PATH%
                    ) else (
                        echo [ERROR] app.py not found at %APP_PATH%
                        exit /b 1
                    )
                """
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
