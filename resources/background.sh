#!/usr/bin/env bash

set -e

cd /equestria/src/website

echo "Starting background tasks"
python manage.py process_tasks