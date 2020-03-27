#!/bin/bash
# A helper script to run docker-compose manage.py file
docker-compose run --rm django ./manage.py $@
