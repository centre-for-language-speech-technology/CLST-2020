#!/usr/bin/env bash

set -e

until pg_isready --host="${POSTGRES_HOST}" --username="${POSTGRES_USER}" --quiet; do
    sleep 1;
done

touch -a /equestria/log/uwsgi.log
touch -a /equestria/log/django.log
touch -a /equestria/log/background_tasks.log

cd /equestria/src/website

./manage.py collectstatic --no-input -v0 --ignore="*.scss"
./manage.py migrate --no-input

chown --recursive www-data:www-data /equestria/
chmod +x /usr/local/bin/uwsgi.sh
chmod +x /usr/local/bin/background.sh

echo "Starting uwsgi server"
sh /usr/local/bin/uwsgi.sh &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start the uwsgi server: $status"
  exit $status
fi

echo "uwsgi server started"
echo "Starting background tasks"
# Start the second process
sh /usr/local/bin/background.sh &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start background tasks: $status"
  exit $status
fi

echo "Background tasks started"
# Naive check runs checks once a minute to see if either of the processes exited.
# This illustrates part of the heavy lifting you need to do if you want to run
# more than one service in a container. The container exits with an error
# if it detects that either of the processes has exited.
# Otherwise it loops forever, waking up every 60 seconds

while sleep 60; do
  ps aux |grep /usr/local/bin/uwsgi.sh |grep -q -v grep
  UWSGI=$?
  ps aux |grep /usr/local/bin/background.sh |grep -q -v grep
  BACKGROUND=$?
  # If the greps above find anything, they exit with 0 status
  # If they are not both 0, then something is wrong
  if [ $UWSGI -ne 0 ]; then
    echo "UWSGI quitted unexpectedly."
    exit 1
  fi
  if [ $BACKGROUND -ne 0 ]; then
  	echo "Background tasks quitted unexpectedly."
  	exit 1
  fi
done
