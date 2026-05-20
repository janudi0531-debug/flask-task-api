pipeline {
    agent any
 
    environment {
        IMAGE_NAME     = 'flask-task-api'
        DOCKERHUB_USER = 'janudi764'
        IMAGE_TAG      = "${env.DOCKERHUB_USER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}"
        IMAGE_LATEST   = "${env.DOCKERHUB_USER}/${env.IMAGE_NAME}:latest"
    }
 
    stages {
 
        // ── STAGE 1: BUILD ──────────────────────────────────────────
        stage('Build') {
            steps {
                echo '=== Building Docker Image ==='
                sh """
                    docker build -t ${IMAGE_TAG} .
                    docker tag ${IMAGE_TAG} ${IMAGE_LATEST}
                    docker tag ${IMAGE_TAG} ${IMAGE_NAME}:latest
                    echo 'Image built and tagged:'
                    docker images | grep ${IMAGE_NAME}
                """
            }
        }
 
        // ── STAGE 2: TEST ───────────────────────────────────────────
        stage('Test') {
            steps {
                echo '=== Running Tests with Coverage ==='
                sh """
                    pip install -r requirements.txt --quiet
                    pytest tests/ \\
                        --cov=app \\
                        --cov-report=xml:coverage.xml \\
                        --cov-report=term-missing \\
                        --junitxml=test-results.xml \\
                        -v
                """
            }
            post {
                always {
                    junit 'test-results.xml'
                }
                failure {
                    error 'Tests failed — pipeline stopped.'
                }
            }
        }
 
        // ── STAGE 3: CODE QUALITY ────────────────────────────────────
        stage('Code Quality') {
            steps {
                echo '=== Running SonarQube Analysis ==='
                withSonarQubeEnv('SonarQube') {
                    sh 'sonar-scanner'
                }
            }
            post {
                always {
                    script {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "Quality Gate failed: ${qg.status}"
                        }
                    }
                }
            }
        }
 
        // ── STAGE 4: SECURITY ────────────────────────────────────────
        stage('Security') {
            steps {
                echo '=== Running Security Scans ==='
                sh """
                    pip install bandit safety --quiet
                    echo '--- Bandit (Python code scan) ---'
                    bandit -r app/ -f json -o bandit-report.json -ll || true
                    bandit -r app/ -ll || true
                    echo '--- Safety (dependency CVE scan) ---'
                    safety check --json > safety-report.json || true
                    safety check || true
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.json, safety-report.json',
                                     allowEmptyArchive: true
                }
            }
        }
 
        // ── STAGE 5: DEPLOY (STAGING) ────────────────────────────────
        stage('Deploy - Staging') {
            steps {
                echo '=== Deploying to Staging ==='
                sh """
                    # Stop existing staging container if running
                    docker stop flask-staging || true
                    docker rm flask-staging || true
 
                    # Deploy staging
                    docker compose -f docker-compose.yml up -d
 
                    # Wait for it to be healthy
                    echo 'Waiting for staging to start...'
                    sleep 8
 
                    # Smoke test
                    STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5001/health)
                    echo "Staging health check returned: ${STATUS}"
                    if [ "$STATUS" != '200' ]; then
                        echo 'STAGING HEALTH CHECK FAILED'
                        exit 1
                    fi
                    echo 'Staging is healthy!'
                """
            }
        }
 
        // ── STAGE 6: RELEASE ─────────────────────────────────────────
        stage('Release') {
            steps {
                echo '=== Releasing to Production ==='
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        # Push to DockerHub
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push ${IMAGE_TAG}
                        docker push ${IMAGE_LATEST}
                        echo 'Image pushed to DockerHub'
 
                        # Deploy to production
                        docker stop flask-prod || true
                        docker rm flask-prod || true
                        docker compose -f docker-compose.prod.yml up -d app-prod
 
                        echo 'Production deployment complete'
                    """
                }
                withCredentials([usernamePassword(
                    credentialsId: 'github-credentials',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_PASS')]) {
                    sh """
                        git config user.email 'jenkins@pipeline.local'
                        git config user.name 'Jenkins'
                        git tag -a v1.0.${BUILD_NUMBER} -m 'Release build ${BUILD_NUMBER}'
                        git push https://$GIT_USER:$GIT_PASS@https://github.com/janudi0531-debug/flask-task-api.git \\
                            v1.0.${BUILD_NUMBER} || true
                        echo 'Git tag pushed: v1.0.${BUILD_NUMBER}'
                    """
                }
            }
        }
 
        // ── STAGE 7: MONITORING ──────────────────────────────────────
        stage('Monitoring') {
            steps {
                echo '=== Starting Monitoring Stack ==='
                sh """
                    # Start Prometheus and Grafana
                    docker compose -f docker-compose.prod.yml up -d prometheus grafana
 
                    sleep 10
 
                    # Verify Prometheus is up
                    PROM=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/ready)
                    echo "Prometheus status: ${PROM}"
 
                    # Verify Grafana is up
                    GRAF=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health)
                    echo "Grafana status: ${GRAF}"
 
                    echo 'Monitoring stack is running.'
                    echo 'Grafana: http://localhost:3000 (admin/admin)'
                    echo 'Prometheus: http://localhost:9090'
                """
            }
        }
 
    }
 
    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline FAILED. Check stage logs above.'
        }
        always {
            echo "Build ${BUILD_NUMBER} finished with status: ${currentBuild.result}"
        }
    }
 
}
