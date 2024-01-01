from dash import DiskcacheManager, CeleryManager
from flask_caching import Cache
import os
import requests_cache

requests_cache.install_cache()

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 86400
}

if 'REDIS_URL' in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(celery_app)
    config['CACHE_TYPE'] = 'RedisCache'
    config['CACHE_KEY_PREFIX'] = 'flask_cache.'
    config['CACHE_REDIS_URL'] = os.environ['REDIS_URL']

else:
    # Diskcache for non-production apps when developing locally
    import diskcache
    cache = diskcache.Cache('./.cache')
    background_callback_manager = DiskcacheManager(cache)
    config['CACHE_TYPE'] = 'FileSystemCache'
    config['CACHE_DIR'] = './.cache'

flask_cache = Cache(config=config)
