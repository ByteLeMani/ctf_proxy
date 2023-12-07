#!/bin/bash
###########

sh -c "/nginxreloader.sh &"
exec "$@"