#!/bin/sh
echo "Starting migrations for project..."
python /code/manage.py makemigrations
python /code/manage.py migrate --noinput
echo "Starting migrations for app..."
python /code/manage.py makemigrations main
python /code/manage.py migrate main --noinput
echo "Migrations ended!"

exec "$@"