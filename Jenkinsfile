// ACEest Fitness API — simple CI-style pipeline for coursework
// Works on Windows Jenkins (bat) and Linux agents (sh).

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
                        bat 'python -m pip install --upgrade pip'
                        bat 'python -m pip install -r requirements.txt'
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
                        bat 'python -m pytest tests/ -v --tb=short'
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
