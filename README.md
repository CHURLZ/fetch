#### Fetcher

#### Setup
__Before first run, run setup_db.py to create DB tables.__
You need RabbitMQ. Install yourself :)
You need celery + other requirements.

`pip install -r requirements.txt`



Run `run.sh` to execute application. This scripts run the following:

    celery -A app.tasks beat -l info
    celery -A app.tasks worker --pool=solo -l info
