#!/bin/bash

docker-compose up -d &&
docker exec -it sequbot-database bash -c "source /entrypoint.sh && restore"
