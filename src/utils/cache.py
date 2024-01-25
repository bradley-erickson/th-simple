from flask_caching import Cache
import os
import requests_cache

# requests_cache.install_cache(backend='filesystem', cache_name='.requests-cache')

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 86400
}

if 'REDIS_URL' in os.environ:
    config['CACHE_TYPE'] = 'RedisCache'
    config['CACHE_KEY_PREFIX'] = 'flask_cache.'
    config['CACHE_REDIS_URL'] = os.environ['REDIS_URL']

else:
    config['CACHE_TYPE'] = 'FileSystemCache'
    config['CACHE_DIR'] = './.cache'

cache = Cache(config=config)
