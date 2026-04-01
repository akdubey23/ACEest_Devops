// ACEest Fitness API — simple CI-style pipeline for coursework
// Works on Windows Jenkins (bat) and Linux agents (sh).
// Windows: scripts/jenkins-windows-ci.cmd finds Python (service account has no user PATH).
// Optional: set job/node env PYTHON_JENKINS=C:\Path\to\python.exe if discovery still fails.

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
                        bat 'call scripts\\jenkins-windows-ci.cmd install'
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
                        bat 'call scripts\\jenkins-windows-ci.cmd test'
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
