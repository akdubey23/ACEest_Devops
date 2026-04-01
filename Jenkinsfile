// ACEest Fitness API — simple CI-style pipeline for coursework
// Works on Windows Jenkins (bat) and Linux agents (sh).
// On Windows, the Jenkins service often has no `python` on PATH; try `py -3` first (python.org launcher).

pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 -m pip install --upgrade pip'
                        sh 'python3 -m pip install -r requirements.txt'
                    } else {
                        bat '''
                            @echo off
                            py -3 --version >nul 2>nul
                            if not errorlevel 1 (
                                py -3 -m pip install --upgrade pip
                                py -3 -m pip install -r requirements.txt
                                exit /b 0
                            )
                            python --version >nul 2>nul
                            if not errorlevel 1 (
                                python -m pip install --upgrade pip
                                python -m pip install -r requirements.txt
                                exit /b 0
                            )
                            python3 --version >nul 2>nul
                            if not errorlevel 1 (
                                python3 -m pip install --upgrade pip
                                python3 -m pip install -r requirements.txt
                                exit /b 0
                            )
                            echo ERROR: Python 3 not on PATH for this Jenkins agent. Install Python for all users with "Add to PATH", or add Scripts folder to the system PATH for the Jenkins service account.
                            exit /b 1
                        '''
                    }
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 -m pytest tests/ -v --tb=short'
                    } else {
                        bat '''
                            @echo off
                            py -3 --version >nul 2>nul
                            if not errorlevel 1 goto :run_py
                            python --version >nul 2>nul
                            if not errorlevel 1 goto :run_python
                            python3 --version >nul 2>nul
                            if not errorlevel 1 goto :run_python3
                            echo ERROR: Python 3 not on PATH.
                            exit /b 1
                            :run_py
                            py -3 -m pytest tests/ -v --tb=short
                            exit /b %ERRORLEVEL%
                            :run_python
                            python -m pytest tests/ -v --tb=short
                            exit /b %ERRORLEVEL%
                            :run_python3
                            python3 -m pytest tests/ -v --tb=short
                            exit /b %ERRORLEVEL%
                        '''
                    }
                }
            }
        }

        stage('Docker build') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'docker build -t aceest-fitness-api:jenkins .'
                    } else {
                        bat 'docker build -t aceest-fitness-api:jenkins .'
                    }
                }
            }
        }
    }
}
