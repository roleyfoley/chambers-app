#!groovy

// Testing pipeline

pipeline {
    agent {
        label 'hamlet-latest'
    }
    options {
        timestamps ()
        buildDiscarder(
            logRotator(
                numToKeepStr: '10'
            )
        )
        disableConcurrentBuilds()
        durabilityHint('PERFORMANCE_OPTIMIZED')
        parallelsAlwaysFailFast()
        skipDefaultCheckout()
    }

    environment {
        DOCKER_BUILD_DIR = "${env.DOCKER_STAGE_DIR}/${BUILD_TAG}"
    }

    parameters {
        string(
            name: 'branchref_intergov',
            defaultValue: 'master',
            description: 'The commit to use for the testing build'
        )
        booleanParam(
            name: 'all_tests',
            defaultValue: false,
            description: 'Run tests for all components'
        )
    }

    stages {
        // intergov required for running full test suite
        stage('Testing') {

            when {
                anyOf {
                    changeRequest()
                    equals expected: true, actual: params.all_tests
                }
            }


            stages {
                stage('Setup intergov') {
                    when {
                        changeRequest()
                    }

                    steps {
                        dir("${env.DOCKER_BUILD_DIR}/test/intergov/") {
                            checkout(
                                [
                                    $class: 'GitSCM',
                                    branches: [[name: "${params.branchref_intergov}" ]],
                                    userRemoteConfigs: [[ url: 'https://github.com/trustbridge/intergov' ]]
                                ]
                            )

                            sh '''#!/bin/bash
                                cp demo-local-example.env demo-local.env
                                python3.6 pie.py intergov.build
                                python3.6 pie.py intergov.start
                                echo "waiting for startup"
                                sleep 60s
                            '''
                        }
                    }
                }

                stage('Setup Chambers') {
                    steps {
                        dir("${env.DOCKER_BUILD_DIR}/test/chambers_app") {
                            checkout scm
                        }

                        dir("${env.DOCKER_BUILD_DIR}/test/chambers_app/src/") {
                            sh '''#!/bin/bash
                            touch local.env
                            docker-compose -f docker-compose.yml -f demo.yml up --build -d
                            sleep 30s
                            '''
                        }
                    }
                }


                stage('Run Testing') {
                    steps {
                        dir("${env.DOCKER_BUILD_DIR}/test/chambers_app/src/") {
                            sh '''#!/bin/bash
                            docker-compose -f docker-compose.yml -f demo.yml run -T django py.test --junitxml=/app/tests/junit.xml
                            docker-compose -f docker-compose.yml -f demo.yml run -T django coverage run -m pytest
                            docker-compose -f docker-compose.yml -f demo.yml run -T django coverage html
                            '''
                        }
                    }

                    post {
                        always {
                            dir("${env.DOCKER_BUILD_DIR}/test/chambers_app/src/"){

                                junit 'tests/*.xml'

                                publishHTML(
                                    [
                                        allowMissing: true,
                                        alwaysLinkToLastBuild: true,
                                        keepAll: true,
                                        reportDir: 'htmlcov',
                                        reportFiles: 'index.html',
                                        reportName: 'Chambers Coverage Report',
                                        reportTitles: ''
                                    ]
                                )
                            }
                        }
                    }
                }
            }

            post {

                cleanup {
                    // Cleanup chambers app
                    dir("${env.DOCKER_BUILD_DIR}/test/chambers_app/src/") {
                        sh '''#!/bin/bash
                            if [[ -f docker-compose.yml ]]; then
                                docker-compose -f docker-compose.yml -f demo.yml down --rmi local -v --remove-orphans
                            fi
                        '''
                    }

                    dir("${env.DOCKER_BUILD_DIR}/test/intergov/") {
                        sh '''#!/bin/bash
                            if [[ -f pie.py ]]; then
                                python3.6 pie.py intergov.destroy
                            fi
                        '''
                    }
                }
            }
        }

    }

    post {
        cleanup {
            cleanWs()
        }
    }
}
