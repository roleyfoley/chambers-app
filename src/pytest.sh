#!/bin/bash
# A helper script to run tests in docker-compose env and
# do some code style/common bugs check

docker-compose run --rm django sh -c "pytest $@ && mypy chambers_app && flake8"
