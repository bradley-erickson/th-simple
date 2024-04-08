#! /bin/sh

# start redis
redis-server --daemonize yes

# start celery & gunicorn
cd src/
celery -A app:celery_app worker &
gunicorn --worker-tmp-dir /dev/shm --timeout 120 app:server
