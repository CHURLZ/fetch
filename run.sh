#!/usr/bin/env bash

celery -A app.tasks beat -l info &
celery -A app.tasks worker --pool=solo -l info
