#!/bin/bash

source venv/bin/activate
uwsgi --socket 0.0.0.0:5000 -w wsgi:app --ini FuelWebsite.ini
