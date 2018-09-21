#!/bin/bash
#-*- coding: utf-8 -*-
set -e

postgres_ready() {
python3 << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(dbname="postgres", user="postgres", password="", host="db")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgresql is unavailable - Waiting..."
  sleep 1
done

#echo "================ CREATING MIGRATIONS =========================="
#python manage.py makemigrations

echo "================ RUNNING MIGRATIONS ==========================="
python manage.py migrate

echo "================ PREPARE STATIC FILES ========================="
python manage.py collectstatic --noinput

echo "================ READY ========================================"
exec "$@"
