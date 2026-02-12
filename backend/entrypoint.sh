#!/bin/sh

flask db migrate
flask db upgrade

exec flask run --host=0.0.0.0 --port=5000
