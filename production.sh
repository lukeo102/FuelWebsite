#!/bin/bash

source venv/bin/activate
uwsgi --socket 192.168.0.101:5000 --protocol=http -w wsgi:app --ini FuelWebsite.ini
