pipeline {
    agent any

    environment {
        IMAGE_NAME     = 'flask-task-api'
        DOCKERHUB_USER = 'janudi764'
        IMAGE_TAG      = "${env.DOCKERHUB_USER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}"
        IMAGE_LATEST   = "${env.DOCKERHUB_USER}/${env.IMAGE_NAME}:latest"
    }

    stages {
	// PIPELINE STAGES

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
                sh '''
                    /var/jenkins_home/venv/bin/pip install -r requirements.txt --quiet
                    /var/jenkins_home/venv/bin/python -m pytest tests/ \
                        --cov=app \
                        --cov-report=xml:coverage.xml \
                        --cov-report=term-missing \
                        --junitxml=test-results.xml \
                        -v
                '''
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
                    script {
                        def scannerHome = tool 'SonarQube Scanner'
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
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
	        sh '''
	            /var/jenkins_home/venv/bin/pip install bandit pip-audit --quiet
	            echo '--- Bandit (Python code scan) ---'
	            /var/jenkins_home/venv/bin/bandit -r app/ -f json -o bandit-report.json -ll || true
	            /var/jenkins_home/venv/bin/bandit -r app/ -ll || true
	            echo '--- pip-audit (dependency CVE scan) ---'
	            /var/jenkins_home/venv/bin/pip-audit > pip-audit-report.txt 2>&1 || true
	            cat pip-audit-report.txt
	        '''
	    }
	    post {
	        always {
	            archiveArtifacts artifacts: 'bandit-report.json, pip-audit-report.txt',
	                             allowEmptyArchive: true
	        }
	    }
	}

        // ── STAGE 5: DEPLOY (STAGING) ────────────────────────────────
        stage('Deploy - Staging') {
            steps {
                echo '=== Deploying to Staging ==='
                sh '''
                    docker stop flask-staging || true
                    docker rm flask-staging || true

                    docker-compose -f docker-compose.yml up -d

                    echo 'Waiting for staging to start...'
                    sleep 8

                    STATUS=$(docker inspect --format="{{.State.Running}}" flask-staging 2>/dev/null)
                    echo "Staging container running: $STATUS"
                    if [ "$STATUS" != "true" ]; then
                        echo 'STAGING CONTAINER FAILED TO START'
                        exit 1
                    fi
                    echo 'Staging is healthy!'
                '''
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
                        echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                        docker push ${IMAGE_TAG}
                        docker push ${IMAGE_LATEST}
                        echo 'Image pushed to DockerHub'

                        docker stop flask-prod || true
                        docker rm flask-prod || true
                        docker-compose -f docker-compose.prod.yml up -d app-prod

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
                        git push https://\$GIT_USER:\$GIT_PASS@github.com/janudi0531-debug/flask-task-api.git v1.0.${BUILD_NUMBER} || true
                        echo 'Git tag pushed: v1.0.${BUILD_NUMBER}'
                    """
                }
            }
        }

        stage('Monitoring') {
	    steps {
	        echo '=== Starting Monitoring Stack ==='
	        sh '''
	            # Only start if not already running
	            if [ "$(docker inspect --format="{{.State.Running}}" prometheus 2>/dev/null)" != "true" ]; then
	                docker stop prometheus || true
	                docker rm prometheus || true
	                docker-compose -f docker-compose.prod.yml up -d prometheus
	            else
                echo "Prometheus already running — skipping restart"
	            fi

	            if [ "$(docker inspect --format="{{.State.Running}}" grafana 2>/dev/null)" != "true" ]; then
	                docker stop grafana || true
	                docker rm grafana || true
	                docker-compose -f docker-compose.prod.yml up -d grafana
	            else
	                echo "Grafana already running — skipping restart"
	            fi

	            sleep 5

	            PROM=$(docker inspect --format="{{.State.Running}}" prometheus 2>/dev/null)
	            echo "Prometheus running: $PROM"

	            GRAF=$(docker inspect --format="{{.State.Running}}" grafana 2>/dev/null)
	            echo "Grafana running: $GRAF"

	            echo "Grafana: http://localhost:3000"
	            echo "Prometheus: http://localhost:9090"
	        '''
	    }
	}
}