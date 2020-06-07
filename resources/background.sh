#!/usr/bin/env bash

set -e

cd /equestria/src/website

echo "Starting background tasks"
sudo -u www-data -E python manage.py process_tasks
