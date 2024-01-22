import datetime
import os
from dotenv import load_dotenv
import requests_cache

load_dotenv()

BASE_URL = 'https://api.trainerhill.com'
# BASE_URL = 'http://localhost:5000'
api_url = f'{BASE_URL}/api'
analysis_url = f'{BASE_URL}/analysis'
api_key = {'x-api-key': os.environ['TRAINER_HILL_API_KEY']}

session = requests_cache.CachedSession(expire_after=datetime.timedelta(1), backend='filesystem', cache_name='.session-cache')
session.headers.update(api_key)

def get_decks(tour_filter):
    url = f'{api_url}/decks'
    r = session.get(url, params=tour_filter)
    if r.status_code == 200:
        return r.json()
    return []
