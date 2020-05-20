#!/usr/bin/env bash

set -e

cd /equestria/src/website

echo "Starting uwsgi server."
uwsgi --chdir=/equestria/src/website \
    --module=equestria.wsgi:application \
    --master --pidfile=/tmp/project-master.pid \
    --socket=:8000 \
    --processes=5 \
    --uid=www-data --gid=www-data \
    --harakiri=20 \
    --post-buffering=16384 \
    --max-requests=5000 \
    --thunder-lock \
    --vacuum \
    --logfile-chown \
    --logto2=/equestria/log/uwsgi.log \
    --ignore-sigpipe \
    --ignore-write-errors \
    --disable-write-exception
