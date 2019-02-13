#!/usr/bin/env

docker-machine create --driver digitalocean \
--digitalocean-access-token $DO_TOKEN \
--digitalocean-region=fra1 \
42rides