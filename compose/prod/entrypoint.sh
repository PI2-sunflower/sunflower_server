#!/bin/bash
#-*- coding: utf-8 -*-
set -e

#echo "================ CREATING MIGRATIONS =========================="
#python manage.py makemigrations

echo "================ RUNNING MIGRATIONS ==========================="
python manage.py migrate

echo "================ PREPARE STATIC FILES ========================="
python manage.py collectstatic --noinput

echo "================ READY ========================================"
exec "$@"
