#!/bin/bash
cd /var/www/HOL-CRM/backend
source venv/bin/activate
exec gunicorn core.wsgi:application -c gunicorn_config.py
